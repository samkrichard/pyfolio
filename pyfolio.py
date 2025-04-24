from pycoingecko import CoinGeckoAPI
import json
import os

PROGRAM_TITLE = 'pyfolio'
VERSION = 'v1.0.0'

DEFAULT_CURRENCY = 'cad'

COLUMN_WIDTH = 22
WIDTH = 5 * COLUMN_WIDTH + 16

# Note: Optimal terminal window width specified in the batch file is given by: 5 * COLUMN_WIDTH + 18

def load_json_file(path, fallback):

    if not os.path.exists(path):
        print(f' Error: \'{path}\' not found.')
        return fallback
    
    with open(path, 'r') as f:
        try:
            return json.load(f)
        
        except json.JSONDecodeError:
            print(f' Error: Failed to parse \'{path}\'.')
            return fallback

def calculate_values(coingeckoapi, currency, portfolio):

    prices = coingeckoapi.get_price(list(portfolio.keys()), currency)
    values = {
        'currency': currency,
        'total' : 0
        }
    
    for coin in portfolio.keys():
        values[coin] = [prices[coin][currency], prices[coin][currency] * portfolio[coin]] 
        values['total'] += values[coin][1]
        
    for coin in portfolio.keys(): 
        values[coin].append(100 * values[coin][1] / values['total'])

    return values

def make_table(values, portfolio):

    headers = (
        'Coin',
        'Total',
        f'Price ({values["currency"].upper()})',
        f'Value ({values["currency"].upper()})',
        '% of Total Value'
        )
    
    table = [['{:<{}}'.format(header, COLUMN_WIDTH) for header in headers],]

    for coin in portfolio.keys():
        table.append([
            '{:<{}}'.format(entree, COLUMN_WIDTH) for entree in [
                coin.replace('-', ' ').title(),
                portfolio[coin],
                '{:<.8f}'.format(values[coin][0]),
                '{:<.8f}'.format(values[coin][1]),
                '{:2.2f}'.format(values[coin][2]) + ' %'
                ]
            ])

    return table

def display_portfolio(coingeckoapi, currency, portfolio):
    values = calculate_values(coingeckoapi, currency, portfolio)
    table = make_table(values, portfolio)
    
    for i in range(len(table) + 3):
        if not (i % (len(table) + 2)) or i == 2:
            print(f' {"="*WIDTH}')
        else:
            print(f' | {" | ".join(["{:<{}}".format(entree, COLUMN_WIDTH) for entree in table[i - 2 + (i < 2)]])} |')
            
    print(' |' + '{:^{}}'.format(f'Total Value ({currency.upper()}): {"{:.2f}".format(values["total"])}', (WIDTH - 2)) + '|')
    print(f' {"="*WIDTH}')

def display_title():
    for i in range(3):
        print((f' {"="*WIDTH}', f' |{"{:^{}}".format(PROGRAM_TITLE + " " + VERSION, WIDTH - 2)}|')[i%2])
    
def display_help():
    print("""
 Press Enter to refresh prices.

 Portfolio information must be manually entered into the program's source file.
 
 Note: When checking against bitcoin, the id must be entered as 'btc'. When Checking the price of
       bitcoin, use 'bitcoin'.

 Commands:

  'help':
      - Display this help screen.

      - Aliases: '?', 'h'
     
  'currency':
      - Change the currently selected currency.
      
      - Alias: 'c'

  'price':
      - Check the price of a cryptocurrency against fiat or bitcoin.
      
      - Alias: 'p'

  'all-in':
      - Calculate the total amount of a cryptocurrency acquired from converting the entire
        portfolio into it.
        
      - Aliases: 'allin', 'a-i', 'ai', 'a' 
     
  'exit':
      - Terminate the program.
      
      - Alias: 'e'""")

def get_user_input(coingeckoapi, currency, portfolio):
    cmd = input('\n >> ').lower().split()
    print()

    if len(cmd) == 0:
        display_portfolio(coingeckoapi, currency, portfolio)            

    elif cmd[0] in ('e', 'exit'):
        print(' Goodbye!\n')
        return False

    elif cmd[0] in ('?', 'help', 'h'):
        display_title()
        display_help()

    elif cmd[0] in ('currency', 'c'):
        currency = cmd[1]
        display_portfolio(coingeckoapi, currency, portfolio)

    elif cmd[0] in ('price', 'p'):
        if len(cmd) > 2:
            prices = coingeckoapi.get_price(cmd[1], cmd[2])
        else:
            prices = coingeckoapi.get_price(cmd[1], currency)
            cmd.append(currency)

        print(f' {cmd[1].replace("-", " ").title()} price: {prices[cmd[1]][cmd[2]]} {cmd[2].upper()}')

    elif cmd[0] in ('all-in', 'allin', 'a-i', 'ai', 'a'):
        values = calculate_values(coingeckoapi, currency, portfolio)
        
        if cmd[1].lower() in portfolio.keys():   
            difference = (values['total'] - values[cmd[1]][1]) / values[cmd[1]][0]
            total = portfolio[cmd[1]] + difference
            
        else:
            difference = values['total'] / coingeckoapi.get_price(cmd[1], currency)[cmd[1]][currency]
            total = difference

        print(f' Total {cmd[1].replace("-", " ").title()}: {total} (+ {difference})')
        
    else:
        print(' Error: Unknown command.')

    return True, currency


def main():
    coingeckoapi = CoinGeckoAPI()
    config = load_json_file('config.json', {})

    if 'default_currency' in config:
        currency = config['default_currency']
    else:
        currency = 'cad'

    portfolio = load_json_file('portfolio.json', {})

    display_title()
    print('\n Welcome!\n')

    display_portfolio(coingeckoapi, currency, portfolio)

    running = True

    print('\n Press Enter to refresh or type \'?\' for help.')
    while (running):
        running, currency = get_user_input(coingeckoapi, currency, portfolio)
        

if __name__ == '__main__':
    main()
