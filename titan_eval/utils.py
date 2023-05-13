import os
import json
import urllib.request

from titan_eval.normalization import normalize_data


def has_domain_predictions(data):
    for dialog in data.values():
        for turn in dialog:
            if "active_domains" not in turn:
                return False
    return True


def get_domain_estimates_from_state(data):

    for dialog in data.values():

        # Use an approximation of the current domain because the slot names used for delexicalization do not contain any
        # information about the domain they belong to. However, it is likely that the system talks about the same domain
        # as the domain that recently changed in the dialog state (which should be probably used for the possible lexicalization). 
        # Moreover, the usage of the domain removes a very strong assumption done in the original evaluation script assuming that 
        # all requestable slots are mentioned only and exactly for one domain (through the whole dialog).

        current_domain = None
        old_state = {}
        old_changed_domains = []

        for turn in dialog:
 
            # Find all domains that changed, i.e. their set of slot name, slot value pairs changed.
            changed_domains = []
            for domain in turn["state"]:
                domain_state_difference = set(turn["state"].get(domain, {}).items()) - set(old_state.get(domain, {}).items())
                if len(domain_state_difference) > 0:
                    changed_domains.append(domain)

            # Update the current domain with the domain whose state currently changed, if multiple domains were changed then:
            # - if the old current domain also changed, let the current domain be
            # - if the old current domain did not change, overwrite it with the changed domain with most filled slots
            # - if there were multiple domains in the last turn and we kept the old current domain & there are currently no changed domains, use the other old domain
            if len(changed_domains) == 0:
                if current_domain is None:
                    turn["active_domains"] = []
                    continue 
                else:
                    if len(old_changed_domains) > 1:
                        old_changed_domains = [x for x in old_changed_domains if x in turn["state"] and x != current_domain]
                        if len(old_changed_domains) > 0:
                            current_domain = old_changed_domains[0] 

            elif current_domain not in changed_domains:
                current_domain = max(changed_domains, key=lambda x: len(turn["state"][x]))

            old_state = turn["state"]
            old_changed_domains = changed_domains
            
            turn["active_domains"] = [current_domain]


def has_state_predictions(data):
    for dialog in data.values():
        for turn in dialog:
            if "state" not in turn:
                return False
    return True


def load_goals():
    dir_path = os.path.dirname(os.path.realpath(__file__))
    with open(os.path.join(dir_path, "data", "goals.json")) as f:
        return json.load(f)


def load_booked_domains():
    dir_path = os.path.dirname(os.path.realpath(__file__))
    with open(os.path.join(dir_path, "data", "booked_domains.json")) as f:
        return json.load(f)


def load_references(systems=['mwz22']): #, 'damd', 'uniconv', 'hdsa', 'lava', 'augpt']):
    references = {}
    for system in systems:
        if system == 'mwz22':
            continue
        dir_path = os.path.dirname(os.path.realpath(__file__))
        with open(os.path.join(dir_path, "data", "references", f"{system}.json")) as f:
            references[system] = json.load(f)
    if 'mwz22' in systems:
        references['mwz22'] = load_titan_reference()
    return references


def load_titan_reference():
    dir_path = os.path.dirname(os.path.realpath(__file__))
    data_path = os.path.join(dir_path, "data", "references", "mwz22.json")
    if os.path.exists(data_path):
        with open(data_path) as f:
            return json.load(f)
    references, _ = load_titan()
    return references


def load_gold_states():
    dir_path = os.path.dirname(os.path.realpath(__file__))
    data_path = os.path.join(dir_path, "data", "gold_states.json")
    if os.path.exists(data_path):
        with open(data_path) as f:
            return json.load(f)
    _, states = load_titan()
    return states

    
def load_titan():
    #
    # def delexicalize_utterance(utterance, span_info):
    #     span_info.sort(key=(lambda  x: x[-2])) # sort spans by start index
    #     new_utterance = ""
    #     prev_start = 0
    #     for span in span_info:
    #         intent, slot_name, value, start, end = span
    #         if start < prev_start or value == "dontcare":
    #             continue
    #         new_utterance += utterance[prev_start:start]
    #         new_utterance += f"[{slot_name}]"
    #         prev_start = end
    #     new_utterance += utterance[prev_start:]
    #     return new_utterance
    def delexicalize_utterance(text):
        delex_sg_valdict_path = 'data/titan-preprocessed/delex_single_valdict.json'
        delex_mt_valdict_path = 'data/titan-preprocessed/delex_multi_valdict.json'
        delex_refs_path = 'data/titan-preprocessed/reference_no.json'
        ambiguous_val_path = 'data/titan-preprocessed/ambiguous_values.json'
        delex_sg_valdict = json.loads(open(delex_sg_valdict_path, 'r').read())
        delex_mt_valdict = json.loads(open(delex_mt_valdict_path, 'r').read())
        delex_refs = json.loads(open(delex_refs_path, 'r').read())
        ambiguous_vals = json.loads(open(ambiguous_val_path, 'r').read())

        text = clean_text(text)

        text = re.sub(r'\d{5}\s?\d{5,7}', '[value_phone]', text)
        text = re.sub(r'\d[\s-]stars?', '[value_stars]', text)
        text = re.sub(r'\$\d+|\$?\d+.?(\d+)?\s(pounds?|gbps?)', '[value_price]', text)
        text = re.sub(r'tr[\d]{4}', '[value_id]', text)
        text = re.sub(
            r'([a-z]{1}[\. ]?[a-z]{1}[\. ]?\d{1,2}[, ]+\d{1}[\. ]?[a-z]{1}[\. ]?[a-z]{1}|[a-z]{2}\d{2}[a-z]{2})',
            '[value_postcode]', text)

        for value, slot in delex_mt_valdict.items():
            text = text.replace(value, '[value_%s]' % slot)
        # delex reference

        for ref in delex_refs:
            text = text.replace(ref, '[value_reference]')

        for value, slot in delex_sg_valdict.items():
            tokens = text.split()
            for idx, tk in enumerate(tokens):
                if tk == value:
                    tokens[idx] = '[value_%s]' % slot
            text = ' '.join(tokens)

        for ambg_ent in ambiguous_vals:
            start_idx = text.find(' ' + ambg_ent)  # ely is a place, but appears in words like moderately
            if start_idx == -1:
                continue
            front_words = text[:start_idx].split()
            ent_type = 'time' if ':' in ambg_ent else 'place'

            for fw in front_words[::-1]:
                if fw in ['arrive', 'arrives', 'arrived', 'arriving', 'arrival', 'destination', 'there', 'reach', 'to',
                          'by', 'before']:
                    slot = '[value_arrive]' if ent_type == 'time' else '[value_destination]'
                    text = re.sub(' ' + ambg_ent, ' ' + slot, text)
                elif fw in ['leave', 'leaves', 'leaving', 'depart', 'departs', 'departing', 'departure',
                            'from', 'after', 'pulls']:
                    slot = '[value_leave]' if ent_type == 'time' else '[value_departure]'
                    text = re.sub(' ' + ambg_ent, ' ' + slot, text)

        text = text.replace('[value_car] [value_car]', '[value_car]')
        return text

    def parse_state(turn):
        state = {}
        for frame in turn["frames"]:  
            domain = frame["service"]
            domain_state = {}
            slots = frame["state"]["slot_values"]
            for name, value in slots.items():
                if "dontcare" in value:
                    continue 
                domain_state[name.split('-')[1]] = value[0]
            
            if domain_state:
                state[domain] = domain_state
            
        return state

    raw_data = []
    raw_data.extend(json.loads(open("data/titan-preprocessed/data.json"), 'r').read())
    mwz22_data = json.loads(open('data/titan-preprocessed/ambiguous_values.json', 'r').read())

    for dialog in raw_data:
        parsed_turns = []
        for i in range(len(dialog["turns"])):
            t = dialog["turns"][i]
            if i % 2 == 0:
                state = parse_state(t)
                continue       
            parsed_turns.append({
                "response" : delexicalize_utterance(t["utterance"]),
                "state" : state
            })           
        mwz22_data[dialog["dialogue_id"].split('.')[0].lower()] = parsed_turns

    normalize_data(mwz22_data)
    
    references, states = {}, {}
    for dialog in mwz22_data:
        references[dialog] = [x["response"] for x  in mwz22_data[dialog]]
        states[dialog] = [x["state"] for x  in mwz22_data[dialog]]

    dir_path = os.path.dirname(os.path.realpath(__file__))
    reference_path = os.path.join(dir_path, "data", "references", "mwz22.json")
    state_path = os.path.join(dir_path, "data", "gold_states.json")

    with open(reference_path, 'w+') as f:
        json.dump(references, f, indent=2)

    with open(state_path, 'w+') as f:
        json.dump(states, f, indent=2)

    return references, states
