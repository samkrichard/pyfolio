from pycoingecko import CoinGeckoAPI
import json
import os

# --- Config ---
PROGRAM_TITLE = 'pyfolio'
VERSION = 'v1.1.0'

DEFAULT_CURRENCY = 'cad'
COLUMN_WIDTH = 22
NUM_COLUMNS = 5  # Coin, Total, Price, Value, % of Total
WIDTH = NUM_COLUMNS * COLUMN_WIDTH + 16  # Full table width


def load_json_file(path, fallback):
    """
    Load and parse a JSON file.
    If the file does not exist or fails to parse, return the provided fallback value.
    """
    if not os.path.exists(path):
        print(f' Error: \'{path}\' not found.')
        return fallback

    try:
        with open(path, 'r') as f:
            return json.load(f)
    except json.JSONDecodeError:
        print(f' Error: Failed to parse \'{path}\'.')
        return fallback


def calculate_values(coingeckoapi, currency, portfolio):
    """
    Fetch the latest prices for all coins in the portfolio, calculate individual values and
    their percentage of the total portfolio.
    Returns a dictionary structure or None if API call fails or total value is zero.
    """
    try:
        prices = coingeckoapi.get_price(list(portfolio.keys()), currency)
    except Exception as e:
        print(f' Error fetching price data: {e}')
        return None

    values = {'currency': currency, 'total': 0}

    for coin in portfolio:
        if coin not in prices or currency not in prices[coin]:
            print(f' Warning: No pricing data found for "{coin}" in {currency.upper()}')
            continue
        price = prices[coin][currency]
        value = price * portfolio[coin]
        values[coin] = [price, value]
        values['total'] += value

    if values['total'] == 0:
        print(' Error: Total value is zero. Check portfolio or currency.')
        return None

    # Add percentage share for each coin
    for coin in values:
        if coin not in portfolio:
            continue
        values[coin].append(100 * values[coin][1] / values['total'])

    return values


def make_table(values, portfolio):
    """
    Generate a 2D list representing the table structure for terminal output.
    Each row corresponds to a coin with relevant info formatted to COLUMN_WIDTH.
    """
    headers = (
        'Coin',
        'Total',
        f'Price ({values["currency"].upper()})',
        f'Value ({values["currency"].upper()})',
        '% of Total Value'
    )

    table = [['{:<{}}'.format(header, COLUMN_WIDTH) for header in headers]]

    for coin in portfolio:
        if coin not in values:
            continue
        table.append([
            '{:<{}}'.format(entry, COLUMN_WIDTH) for entry in [
                coin.replace('-', ' ').title(),
                portfolio[coin],
                '{:<.8f}'.format(values[coin][0]),
                '{:<.8f}'.format(values[coin][1]),
                '{:2.2f}'.format(values[coin][2]) + ' %'
            ]
        ])
    return table


def display_portfolio(coingeckoapi, currency, portfolio):
    """
    Calculate and display the user's portfolio in a formatted table.
    """
    values = calculate_values(coingeckoapi, currency, portfolio)
    if not values:
        return

    table = make_table(values, portfolio)

    for i in range(len(table) + 3):
        if not (i % (len(table) + 2)) or i == 2:
            print(f' {"=" * WIDTH}')
        else:
            print(f' | {" | ".join(["{:<{}}".format(entry, COLUMN_WIDTH) for entry in table[i - 2 + (i < 2)]])} |')

    decimals = "{:.2f}" if currency in ("usd", "cad") else "{:.8f}"
    print(' |' + '{:^{}}'.format(f'Total Value ({currency.upper()}): {decimals.format(values["total"])}', WIDTH - 2) + '|')
    print(f' {"=" * WIDTH}')


def display_title():
    """
    Display the program title and version centered.
    """
    for i in range(3):
        print((f' {"=" * WIDTH}', f' |{"{:^{}}".format(PROGRAM_TITLE + " " + VERSION, WIDTH - 2)}|')[i % 2])


def display_help():
    """
    Show help instructions for all supported commands.
    """
    print("""
 Press Enter to refresh prices.

 Portfolio information must be manually entered into the program's source file.

 Note: When checking against bitcoin, the id must be entered as 'btc'. When checking the price of
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
      - Aliases: 'allin', 'a-i', 'ai'

  'exit':
      - Terminate the program.
      - Alias: 'e'
    """)


def get_clean_input():
    """
    Get clean, lowercased, split user input.
    """
    return input('\n >> ').strip().lower().split()


def get_user_input(coingeckoapi, currency, portfolio):
    """
    Handle user input and execute corresponding actions.
    """
    cmd = get_clean_input()
    print()

    if not cmd:
        display_portfolio(coingeckoapi, currency, portfolio)
        return True, currency

    if cmd[0] in ('e', 'exit'):
        print(' Goodbye!\n')
        return False, currency

    elif cmd[0] in ('?', 'help', 'h'):
        display_title()
        display_help()

    elif cmd[0] in ('currency', 'c'):
        if len(cmd) < 2:
            print(" Error: Missing currency argument.")
        else:
            currency = cmd[1]
            display_portfolio(coingeckoapi, currency, portfolio)

    elif cmd[0] in ('price', 'p'):
        if len(cmd) < 2:
            print(" Error: Specify a coin name.")
            return True, currency

        coin = cmd[1]
        target_currency = cmd[2] if len(cmd) > 2 else currency

        try:
            prices = coingeckoapi.get_price(coin, target_currency)
            print(f' {coin.replace("-", " ").title()} price: {prices[coin][target_currency]} {target_currency.upper()}')
        except Exception as e:
            print(f' Error fetching price for {coin}: {e}')

    elif cmd[0] in ('all-in', 'allin', 'a-i', 'ai'):
        if len(cmd) < 2:
            print(" Error: Specify a target coin.")
            return True, currency

        values = calculate_values(coingeckoapi, currency, portfolio)
        if not values:
            return True, currency

        target = cmd[1]
        try:
            if target in values:
                difference = (values['total'] - values[target][1]) / values[target][0]
                total = portfolio[target] + difference
            else:
                target_price = coingeckoapi.get_price(target, currency)[target][currency]
                difference = values['total'] / target_price
                total = difference

            print(f' Total {target.replace("-", " ").title()}: {total} (+ {difference})')
        except Exception as e:
            print(f' Error calculating all-in conversion: {e}')

    else:
        print(' Error: Unknown command.')

    return True, currency


def main():
    """
    Main program loop: load config/portfolio, display welcome screen, run command loop.
    """
    coingeckoapi = CoinGeckoAPI()
    config = load_json_file('config.json', {})
    currency = config.get('default_currency', DEFAULT_CURRENCY)

    portfolio = load_json_file('portfolio.json', {})
    if not portfolio:
        print(' Warning: Portfolio is empty.')

    display_title()
    print('\n Welcome!\n')
    display_portfolio(coingeckoapi, currency, portfolio)

    print('\n Press Enter to refresh or type \'?\' for help.')
    running = True
    while running:
        running, currency = get_user_input(coingeckoapi, currency, portfolio)


if __name__ == '__main__':
    main()
