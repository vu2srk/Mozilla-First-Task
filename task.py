import sys, os
import urllib
from bugzilla.agents import BMOAgent
from bugzilla.utils import get_credentials

def query_url_to_dict(url):
    fields_and_values = url.split("?")[1].split(";")
    d = {}

    for pair in fields_and_values:
        (key,val) = pair.split("=")
        if key != "list_id":
            d[key]=urllib.unquote(val)
    
    d["include_fields"] = "_default, attachments, history"

    return d

if __name__ == '__main__':

    query = sys.argv[1]
    
    if query == None:
        sys.exit("Please specify a query")
    
    username, password = get_credentials()
    
    # Load our agent for BMO
    bmo = BMOAgent(username, password)
    
    # Get the buglist(s)
    # import the query
    buglist = []

    if os.path.exists(query):
        info = {}
        execfile(query, info)
        query_name = info['query_name']
        if info.has_key('query_url'):
            buglist = bmo.get_bug_list(query_url_to_dict(info['query_url'])) 
        else:
            print "Error - no valid query params or url in the config file"
            sys.exit(1)
    else:
        print "Not a valid path: %s" % query
    total_bugs = len(buglist)

    print "Found %s bugs" % (total_bugs)

added_list = {}
removed_list = {}

for bug in buglist:
    for changes in bug.history:
        for change in changes.changes:
            if change.field_name == "cf_tracking_firefox17":
                print str(bug.id) + ", " + str(changes.change_time) + ", " + change.field_name + ", " + change.added + ", " + change.removed
                key = str(changes.change_time).strip().split(" ")[0].strip()
                if change.added.strip() == "+":
                    if key in added_list:
                        added_list[key] = added_list[key] + 1
                    else:
                        added_list[key] = 1
                if change.added.strip() == "-":
                    if key in removed_list:
                        removed_list[key] = removed_list[key] + 1
                    else:
                        removed_list[key] = 1

for added in sorted(added_list.iterkeys()):
    print str(added) + ", " + str(added_list[added]) + ", " + (str(removed_list[added]) if added in removed_list else "0") 

for removed in sorted(removed_list.iterkeys()):
    if removed not in added_list:
        print str(removed) + ", " + "0, " + str(removed_list[removed])
