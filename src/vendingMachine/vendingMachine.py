"""Python vending machine"""

import time, sys

try:
    import openpyxl
except ModuleNotFoundError:
    print('This program requires openpyxl module, install it with pip')
    sys.exit()

# this vending machine is going to use Polish national currency called "Polish zloty" (code: PLN)
# available coin nominals are 1gr, 2gr, 5gr, 10gr, 20gr, 50gr, 1zl, 2zl, 5zl
# this vending machine wont accept coins with denominations smaller than 10gr
COINS = [0.1, 0.2, 0.5, 1, 2, 5]
WALLET = 20

print('Welcome to vending machine.')

def main():
    
    print('Purchase snacks using their corresponding numbers.\nWe have:')
    snacks_pc, snacks_qt = getSnacks()[0], getSnacks()[1]
    snacks = snacks_pc.keys()
    snacks_list = []
    bought_snacks = []

    for index, item in enumerate(snacks):
        snacks_list.append(item)
        print(index,':', item, end=' | ')
    print('')
    
    pickSnack(bought_snacks, snacks, snacks_pc, snacks_qt, snacks_list)

    print('What would you like to do now?')
    while True:
        print('''You can:
    1. Make another purchase
    2. Refund your purchase
    3. Enter service mode
    4. Quit''')
        response = input('> ')

        if response.isdecimal() and int(response) in range(1, 5):
            response = int(response)
            if response == 1:
                main()
            elif response == 2:
                getRefund(bought_snacks, snacks, snacks_list, snacks_pc, snacks_qt)
            elif response == 3:
                serviceMode()
            else:
                print('Goodbye, have a nice day')
                sys.exit()

        else:
            print('Invalid input, try again')
            continue
    
def getSnacks():

    try:
        snacks_wb = openpyxl.load_workbook('snacks.xlsx')
    except FileNotFoundError:
        print('Snacks spreadsheet not found, ensure its in the same directory as program')
        sys.exit()
    
    snacks_sh = snacks_wb['Sheet1']
    snacks_price = {}
    snacks_quantity = {}

    for name, price, quantity in zip(snacks_sh['A'], snacks_sh['B'], snacks_sh['C']):
        snacks_price[name.value] = price.value
        snacks_quantity[name.value] = quantity.value
        
    return snacks_price, snacks_quantity

def pickSnack(bought_snacks, snacks, snacks_pc, snacks_qt, snacks_list):

    global WALLET

    while True:
        
        if WALLET == 0:
            print('You are out of money')
            sys.exit()
        
        print('What do you want to buy?')
        print(f'You have {round(WALLET, 2)} PLN left')
        echo = input('> ')

        if echo.isdecimal() and 0 <= int(echo) <= len(snacks)-1:
            snack_id = int(echo)
            if snacks_qt[snacks_list[snack_id]] == 0:
                print(f'We are out of {snacks_list[snack_id]}.\nPick something else.')
                continue
            break
        else:
            print('Invalid input, try again')
    
    snack_name = snacks_list[snack_id] 
    snack_pc = float(snacks_pc[snacks_list[snack_id]])

    buySnacks(bought_snacks, snack_id, snack_name, snack_pc, snacks_qt)

    return snack_name, snack_pc

def buySnacks(bought_snacks, snack_id, snack_name, snack_pc, snacks_qt):

    global WALLET

    print(f'You\'ve chosen {snack_name}, which costs {snack_pc} PLN')
    print('Please insert proper amount of coins or (C)ancel your purchase')
    
    pay = 0

    while pay != snack_pc:

        print(f'{round(snack_pc-pay, 2)} PLN left to pay')
        amount = input('> ')
        if amount.upper().startswith('C'):
            print('Canceling purchase')
            WALLET += pay
            main()

        try:
            amount = round(float(amount), 2)
        except ValueError:
            print('Invalid amount, try again')
            continue

        if amount in COINS:
            pay += amount
            WALLET -= amount
            if pay < snack_pc:
                continue
            
            else:
                change = round(pay-snack_pc, 2)
                print(f'You\'ve inserted {change} PLN too much.\nReturning change.')
                pay -= change
                WALLET += change
                
        else:
            print('Unrecognized coin. Insert Polish zloty nominals')            

    
    snacks_qt[snack_name] -= 1
    bought_snacks += [snack_id]

    print('Purchase confirmed.\nPlease hold', end=' ')
    for dot in range(3):
        time.sleep(1)
        print('.', end=' ')
    print('\nHere is your snack!')
    print(f'****{snack_name.upper()}****')
    return WALLET

def getRefund(bought_snacks, snacks, snacks_list, snacks_pc, snacks_qt):
    
    global WALLET

    print('What snack do you want to refund?')
    for index, item in enumerate(snacks):
        print(index,':', item, end=' | ')
    print('')

    while True:
        refunded_snack = input('> ')
        if refunded_snack.isdecimal():
            if int(refunded_snack) in bought_snacks:
                refunded_snack = int(refunded_snack)
                break
            elif not int(refunded_snack) in bought_snacks and int(refunded_snack) in range(len(snacks)+1):
                print('You didn\'t bought this snack yet.\nYou have only bought:')
                for id in bought_snacks:
                    print(f'{snacks_list[id]}, ', end=' ')
                print('\nPick again')
                continue
            else:
                print('There is no such snack under this number.\nTry again.')
                continue 
        else:
            print('Invalid input, pick correct snack number')
            continue
    
    print('Refund accepted.\nPlease hold', end=' ')
    for dot in range(3):
        time.sleep(1)
        print('.', end=' ')
    print(f'\nYou\'ve returned {snacks_list[refunded_snack]}')
    snack_pc = float(snacks_pc[snacks_list[refunded_snack]])
    WALLET += snack_pc
    print(f'{snack_pc} PLN refunded.')
    snacks_qt[snacks_list[refunded_snack]] += 1
    
    if len(bought_snacks) > 0:
        print('Do you want to refund another snack? (Y)es or (N)o')
        while True:
            response = input('> ')
            if response.upper().startswith('Y'):
                getRefund()
    else:
        main()

def serviceMode():
    print('*****SERVICE MODE*****')
    main()

if __name__ == '__main__':
    main()