import json

from pymongo import MongoClient, ReturnDocument, DESCENDING
import config

client = MongoClient(config.MONGO_URL)
db = client['Zerpmon']


def save_new_zerpmon(zerpmon):
    zerpmon_collection = db['MoveSets']
    print(zerpmon)

    doc_str = json.dumps(zerpmon)
    zerpmon = json.loads(doc_str)

    result = zerpmon_collection.update_one(
        {'name': zerpmon['name']},
        {'$set': zerpmon},
        upsert=True)

    if result.upserted_id:
        print(f"Created new Zerpmon with id {result.upserted_id}")
        return f"Successfully added a new Zerpmon {zerpmon['name']}"
    else:
        print(f"Updated Zerpmon with name {zerpmon['name']}")
        return f"Successfully updated Zerpmon {zerpmon['name']}"


def update_all_zerp_moves():
    for document in db['MoveSets'].find():
        if 'level' in document and document['level'] / 10 >= 1 and document['name'] == 'Sapple':
            print('Sapple')
            miss_percent = float([i for i in document['moves'] if i['color'] == 'miss'][0]['percent'])
            percent_change = 3.33 * (document['level'] // 10)
            percent_change = percent_change if percent_change < miss_percent else miss_percent
            count = len([i for i in document['moves'] if i['name'] != ""]) - 1
            print(document)
            for i, move in enumerate(document['moves']):
                if move['color'] == 'miss':
                    move['percent'] = str(round(float(move['percent']) - percent_change, 2))
                    document['moves'][i] = move
                elif move['name'] != "" and float(move['percent']) > 0:
                    move['percent'] = str(round(float(move['percent']) + (percent_change / count), 2))
                    document['moves'][i] = move
            del document['_id']
            save_new_zerpmon(document)


update_all_zerp_moves()
