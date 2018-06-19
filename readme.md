
# TOP8Draft Web API documentation
### Example of console client is in this repo.


All requests are POST, all request parameter types are string, all request return value of the same type - current draft state. Cards are referenced by *multiverseid* from database by mtgjson.com

**http://www.top8draft.com/api/start_draft** - starts a new draft.
Request parameters:
1. **format** - Mtg expansion codes separated by '_'. E.g. "XLN_XLN_XLN"
2. **bots** - 'True' or 'False', separated by ','. True = this player is bot, False = this player is human. E.g. "False,True,True,True,True,True,True,True"
3. **player_names** - names of players, separated by ','. E.g. "me,bot1,bot2,bot3,bot4,bot5,bot6,bot7".

**Return value**: JSON-encoded current draft state

**http://www.top8draft.com/api/make_pick** - saves pick made by player on the server and makes bot picks which became possible after this pick
Params:
1. **id** - draft id
2. **pick_num** - 0-based number of current pick in the round (0-14).
3. **player_pos** - 0-based position of a player who made this pick in the original *player_names* list
4. **pick_pos** - 0-based position of a chosen card in the pack

**Return value**: JSON-encoded current draft state

**http://www.top8draft.com/api/get_draft** - gets current draft state
Params:
1. **id** - draft id

**Return value**: JSON-encoded current draft state


Draft state contents:
1. **id**: id of the draft.
2. **date_played**: date in format "DD/MM/YY" when this draft was finished. None for ongoing drafts.
3. **boosters**: list of MTG expansion codes of boosters in draft.
4. **pack_num**: 0-based integer, current round number. If pack_num = len(boosters) then it means draft is over.
5. **player_names**: list of player names set at the beginning of the draft.
6. **bots**: list of boolean set at the beginning of the draft. Information whether web service should make picks for that player or wait for external input.
7. **packs**: integer matrix of shape (3, 8, 15) (<number of packs in draft>, <number of players in draft>, 15). Each element is *multiverseid* of a card in the packs generated for draft. Contents of this matrix remains the same during draft (it doesn't track picks made by player, it only stores starting point).
8. **foils**: boolean matrix of the same shape. Indicates which cards in packs are foil.
9. **picks**: integer matrix of the same shape. Each element is either 0 (means that pick wasn't made yet) or 1-based position of a chosen card in the pack.
10. **scores**: real-valued matrix of shape (3, 8, 15, 15). Each element is a score assigned to each card in pack for each pick. If that pick wasn't made yet, then all elements in corresponding line would be 0. Score for missing cards set to -100.0
}





## Big thanks to www.mtgjson.com project for their card database