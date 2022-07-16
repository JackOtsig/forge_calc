import json, os, urllib.request


def get_json_data(file):
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    fname = ".\\"+file+".json"
    with open(fname, 'r') as f:
        data = json.load(f)
        f.close()
        return data

def write_to_json(data, file):
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    fname = ".\\"+file+".json"
    with open(fname, 'w') as f:
        json.dump(data, f)
        f.close()


def get_item_data():
    with urllib.request.urlopen('https://api.hypixel.net/resources/skyblock/items') as request:
        data = json.loads(request.read().decode())
    return data

def id_to_name(con, id):
    for item in con["items"]:
        if item['id'] == id:
            return item["name"]

def get_bz_data():
    with urllib.request.urlopen('https://api.hypixel.net/skyblock/bazaar') as request:
        data = json.loads(request.read().decode())
    return data

def get_ah_data(page):
    with urllib.request.urlopen('https://api.hypixel.net/skyblock/auctions?page='+str(page)) as request:
        data = json.loads(request.read().decode())
    return data

def get_all_ah_data():
    iterator = 1
    data = []
    data0 = get_ah_data(0)
    total_pages = data0["totalPages"]
    data.append(data0)
    while iterator < total_pages:
        data.append(get_ah_data(iterator))
        print("page", iterator, "added of", total_pages)
        iterator += 1
    print('done!')
    os.system('cls' if os.name == 'nt' else 'clear')
    return data

def lower_than(int1,int2):
    if int1 < int2 :
        return int1
    else:
        return int2

def get_lbin_data(data):
    BINs = {}
    for page in data:
        for auction in page["auctions"]:
            if auction['bin'] == True:
                name = auction['item_name']
                if name not in BINs:
                    BINs[name] = {}
                    BINs[name]['lbin'] = 999999999999
                price = auction['starting_bid']
                lbin = BINs[name]['lbin']
                BINs[name]['lbin'] = lower_than(price,lbin)
    return BINs

def update_prices():
    ing_list = get_json_data("ingredient_list")
    bz_data = get_bz_data()
    ah_raw_data = get_all_ah_data()
    item_data = get_item_data()
    ah_lbin_data = get_lbin_data(ah_raw_data)
    items = list(ing_list.keys())
    for item in items:
        if ing_list[item]["type"] == "bz":
            ing_list[item]["price"] = bz_data['products'][item]['buy_summary'][0]['pricePerUnit']
        elif ing_list[item]["type"] == "ah":
            item_name = id_to_name(item_data, item)
            for auction in ah_lbin_data:
                if item_name in auction:
                    ing_list[item]["price"] = ah_lbin_data[auction]['lbin']
    write_to_json(ing_list, 'ingredient_list')

def calc_ptc(tier):
    final_dict = {}
    recipe_book = get_json_data('recipe_book')
    ingredient_list = get_json_data('ingredient_list')
    for category in recipe_book:
        for recipe in recipe_book[category]:
            components = []
            time = recipe_book[category][recipe]['time']
            recipe_tier = recipe_book[category][recipe]['tier']
            if recipe_tier > tier:
                continue
            product_price = ingredient_list[recipe]['price']
            comp_price = 0
            for component in recipe_book[category][recipe]['comp']:
                amount = recipe_book[category][recipe]['comp'][component]
                in_comp_price = ingredient_list[component]['price']
                comp_data = (component, in_comp_price, amount)
                poac = in_comp_price * amount
                comp_price += poac
                profit = product_price - comp_price
                if time == 0.08:
                    float(profit) * time
                elif time == 0:
                    pph = profit
                else:
                    pph = float(profit) / time
                    
                components.append(comp_data)
            final_dict[recipe] = (comp_price, product_price, profit, pph, time, components)
    return final_dict

def print_data(data, sort):
    if sort == 'pph':
        sort_num = 3
    sorted_keys = sorted(data, key=lambda x: (data[x][sort_num]))
    for key in sorted_keys:
        print(key,'\n', 'price of components: ', "{:,}".format(int(data[key][0])), '\n', 'sell price: ', "{:,}".format(int(data[key][1])), '\n', 'total profit : ', "{:,}".format(int(data[key][2])), '\n', 'profit per hour: ', "{:,}".format(int(data[key][3])), '\n', 'forge time in hours: ', data[key][4], '\n\n', 'components: ')
        for component in data[key][5]:
            print('  ',component[0]+':' '\n', '    price: ', "{:,}".format(int(component[1])), '\n', '    amount: ', component[2])
        print('\n\n')

def main(tier, sort):
    #update_prices()
    profit_dict = calc_ptc(tier)
    print_data(profit_dict, sort)
if __name__ == "__main__":
    main(7, 'pph')