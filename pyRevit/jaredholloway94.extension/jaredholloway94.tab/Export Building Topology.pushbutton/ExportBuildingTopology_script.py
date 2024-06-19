from Autodesk.Revit.DB import *
import json
import pyrevit

doc = pyrevit._DocsGetter().doc

STAIRS_BASE_LEVEL_PARAM_ID = ElementId(BuiltInParameter.STAIRS_BASE_LEVEL_PARAM)
STAIRS_TOP_LEVEL_PARAM_ID = ElementId(BuiltInParameter.STAIRS_TOP_LEVEL_PARAM)

RoomCollector = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Rooms).WhereElementIsNotElementType()
DoorCollector = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Doors).WhereElementIsNotElementType()
StairCollector = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Stairs).WhereElementIsNotElementType()

phase = doc.Phases[1]


def get_stair_rooms(base_level, top_level, bbox):

	bbox_center = (bbox.Min + bbox.Max)/2
	base_point = XYZ(bbox_center[0], bbox_center[1], (base_level.Elevation + 1))
	top_point = XYZ(bbox_center[0], bbox_center[1], (top_level.Elevation + 1))

	base_room_id = 'Room: 000'
	top_room_id = 'Room: 000'

	for room in RoomCollector:

		if room.IsPointInRoom(base_point):
			base_room_id = f'Room: {room.Number}'

		if room.IsPointInRoom(top_point):
			top_room_id = f'Room: {room.Number}'

	return base_room_id,top_room_id



rooms = {}
for room in RoomCollector:
	rooms[f'Room: {room.Number}'] = {'doors':[],'stairs':[]}


doors = {}
for door in DoorCollector:
	door_mark = door.LookupParameter('Mark').AsValueString()
	door_id = f'Door: {door_mark}'

	if door.get_FromRoom(phase):
		from_room_id = f'Room: {door.get_FromRoom(phase).Number}'
	else:
		from_room_id = 'Room: 000'

	if door.get_ToRoom(phase):
		to_room_id = f'Room: {door.get_ToRoom(phase).Number}'
	else:
		to_room_id = 'Room: 000'

	rooms[from_room_id]['doors'].append(door_id)
	doors[door_id] = {'rooms':[to_room_id]}


stairs = {}
for stair in StairCollector:
	stair_mark = stair.LookupParameter('Mark').AsValueString()

	# 	normal (non-multistory) stair	or	multistory stair with only 1 group
	if (stair.MultistoryStairsId == -1) or (len(stair.GetSubelements()) == 0):

		base_level = doc.GetElement(stair.LookupParameter('Base Level').AsElementId())
		top_level = doc.GetElement(stair.LookupParameter('Top Level').AsElementId())
		bbox = stair.get_BoundingBox(None)
		base_room_id, top_room_id = get_stair_rooms(base_level,top_level,bbox)

		stair_level = base_level.Name
		stair_id = f'Stair: {stair_mark}-L{stair_level[-1]}'

		rooms[top_room_id]['stairs'].append(stair_id)
		stairs[stair_id] = {'rooms':[]}
		stairs[stair_id]['rooms'].append(base_room_id)

	# multistory stair with >1 group
	else:
		sub_stairs = stair.GetSubelements()

		for sub_stair in sub_stairs:

			base_level = doc.GetElement(sub_stair.GetParameterValue(STAIRS_BASE_LEVEL_PARAM_ID).Value)
			top_level = doc.GetElement(sub_stair.GetParameterValue(STAIRS_TOP_LEVEL_PARAM_ID).Value)
			bbox = sub_stair.GetBoundingBox(doc.ActiveView)
			base_room_id, top_room_id = get_stair_rooms(base_level,top_level,bbox)

			stair_level = base_level.Name
			stair_id = f'Stair: {stair_mark}-L{stair_level[-1]}'

			rooms[top_room_id]['stairs'].append(stair_id)
			stairs[stair_id] = {'rooms':[]}
			stairs[stair_id]['rooms'].append(base_room_id)


with open('rooms.json','w') as jsonfile:
	json.dump(rooms,jsonfile)

with open('doors.json','w') as jsonfile:
	json.dump(doors,jsonfile)

with open('stairs.json','w') as jsonfile:
	json.dump(stairs,jsonfile)