from generator import generate

try:
    count = int(input("ВВЕДИТЕ КОЛИЧЕСТВО ГЕНЕРАЦИЙ\n"))
    chain = str(input("ВВЕДИТЕ SOL, EVM, APTOS или BTC в зависимости какие кошельки вам нужны\n")).upper()
    if chain == "BTC":
        bip = str(input("ВВЕДИТЕ СТАНДАРТ ГЕНЕРАЦИИ BIP44 или BIP49 или BIP84\n")).upper()
        generate(count=count, chain = chain, bip = bip)
    else:
        generate(count=count, chain = chain)
except:
    generate()
