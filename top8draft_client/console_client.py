import json
import requests
import sys
from collections import defaultdict
from time import sleep

IP = "www.top8draft.com"

URL_START_DRAFT = "http://{}/api/start_draft/".format(IP)
URL_MAKE_PICK = "http://{}/api/make_pick/".format(IP)
URL_GET_DRAFT = "http://{}/api/get_draft/".format(IP)


BOTS = ",".join(["False"]+["True"]*7)
PLAYER_NAMES = ",".join(['human']+["bot{}".format(i) for i in range(1,8)])
HUMAN_PLAYER_POS = 0

def run():
    with open("AllSets.json", "rt") as f:
        database = json.load(f)
    format = raw_input("Input format name: ")
    boosters = format.split("_")
    response = requests.post(URL_START_DRAFT, data={'format': format, 'bots': BOTS, 'player_names': PLAYER_NAMES})
    draft = json.loads(response.text)
    while True:
        if draft['pack_num'] == len(boosters):
            sys.stdout.write("Draft has ended!\n")
            deck, card_expansions = get_deck(draft, HUMAN_PLAYER_POS, boosters)
            print_deck(deck, card_expansions, database)
            break
        current_packs = get_current_packs(draft)
        if len(current_packs[HUMAN_PLAYER_POS]) == 0 or sum(current_packs[HUMAN_PLAYER_POS][0])==0:
            sleep(0.5)
            response = requests.post(URL_GET_DRAFT, data={'id': draft['id']})
            draft = json.loads(response.text)
            continue
        sys.stdout.write("Current pack:\n")
        card_mapping = print_pack(current_packs[HUMAN_PLAYER_POS][0], database[boosters[draft['pack_num']]])
        pick_pos = raw_input("Which card do you pick ({}-{})? ".format(1, len(card_mapping)))
        pick_pos = card_mapping[int(pick_pos)-1]
        response = requests.post(URL_MAKE_PICK, data={'id': draft['id'], 'pick_num': get_pick_num(draft, HUMAN_PLAYER_POS), 'player_pos': HUMAN_PLAYER_POS, 'pick_pos': pick_pos})
        draft = json.loads(response.text)


#return dict <player_pos> -> <list of packs queued for him>
def get_current_packs(draft):
    packs = dict()
    for player_pos, pack in enumerate(draft['packs'][draft['pack_num']]):
        packs[player_pos] = [pack[:]]
    for pick_num in range(15):
        for player_pos in range(len(draft['player_names'])):
            if draft['picks'][draft['pack_num']][player_pos][pick_num]!=0:
                current_pack = packs[player_pos].pop(0)
                current_pack[draft['picks'][draft['pack_num']][player_pos][pick_num]-1] = 0
                if draft['pack_num']%2==0:
                    pack_pos = (player_pos+1)%len(draft['player_names'])
                else:
                    pack_pos = (player_pos-1)%len(draft['player_names'])
                packs[pack_pos].append(current_pack)
    return packs


def print_pack(pack, expansion):
    card_mapping = []
    for card_pos, card_id in enumerate(pack):
        if card_id == 0:
            continue
        card_mapping.append(card_pos)
        card_title = next(card['name'] for card in expansion['cards'] if card['multiverseid']==card_id)
        sys.stdout.write("{}) {}\n".format(len(card_mapping), card_title))
    return card_mapping


def get_pick_num(draft, player_pos):
    result = 0
    for pick_pos in draft['picks'][draft['pack_num']][player_pos]:
        if pick_pos!=0:
            result +=1
    return result


def get_deck(draft, player_pos, boosters):
    result = defaultdict(int)
    card_expansions = dict()
    for pack_num, expansion in enumerate(boosters):
        for pick_num in range(len(draft['picks'][pack_num][player_pos])):
            pick_pos = draft['picks'][pack_num][player_pos][pick_num]
            if pick_pos == 0:
                continue
            if pack_num%2 == 0:
                original_pack_pos = (player_pos-pick_num)%(len(draft['picks'][pack_num]))
            else:
                original_pack_pos = (player_pos+pick_num)%(len(draft['picks'][pack_num]))
            pack = draft['packs'][pack_num][original_pack_pos]
            result[pack[pick_pos-1]] += 1
            card_expansions[pack[pick_pos-1]] = expansion
    return result, card_expansions


def print_deck(deck, card_expansions, database):
    for card_id, card_num in deck.items():
        card_title = next(card['name'] for card in database[card_expansions[card_id]]['cards'] if card['multiverseid']==card_id)
        sys.stdout.write("{} {}\n".format(card_num, card_title))




if __name__ == "__main__":
    run()