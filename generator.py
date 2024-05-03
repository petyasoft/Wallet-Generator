from bip_utils import Bip39SeedGenerator, Bip44Coins, Bip44, Bip44Changes, base58, Bip49, Bip49Coins, Bip84, Bip84Coins
from mnemonic import Mnemonic
import pandas as pd
from loguru import logger
import os


class EVM():
    def __init__(self, mnemonic, coin_type=Bip44Coins.ETHEREUM, password = '') -> None:
        self.mnemonic = mnemonic.strip()
        self.coin_type = coin_type
        self.password = password 

    def get_address(self):
        seed_bytes = Bip39SeedGenerator(self.mnemonic).Generate(self.password)
        bip44_mst_ctx = Bip44.FromSeed(seed_bytes, self.coin_type).Purpose().Coin().Account(0).Change(Bip44Changes.CHAIN_EXT).AddressIndex(0)
        return {"mnemonic" : self.mnemonic,
                "address" : bip44_mst_ctx.PublicKey().ToAddress(),
                "private" : f"0x{bip44_mst_ctx.PrivateKey().Raw().ToHex()}"}

class SOLANA():
    def __init__(self, mnemonic, coin_type=Bip44Coins.SOLANA, password = '') -> None:
        self.mnemonic = mnemonic.strip()
        self.coin_type = coin_type
        self.password = password 

    def get_address(self):
        seed_bytes = Bip39SeedGenerator(self.mnemonic).Generate(self.password)
        bip44_mst_ctx = Bip44.FromSeed(seed_bytes, self.coin_type)
        bip44_acc_ctx = bip44_mst_ctx.Purpose().Coin().Account(0)
        bip44_chg_ctx = bip44_acc_ctx.Change(Bip44Changes.CHAIN_EXT) # if you use "Solflare", remove this line and make a simple code modify and test
        priv_key_bytes = bip44_chg_ctx.PrivateKey().Raw().ToBytes()
        public_key_bytes = bip44_chg_ctx.PublicKey().RawCompressed().ToBytes()[1:]
        key_pair = priv_key_bytes+public_key_bytes
        return {"mnemonic" : self.mnemonic,
                "address" : bip44_chg_ctx.PublicKey().ToAddress(),
                "private" : base58.Base58Encoder.Encode(key_pair)}

class BTC():
    def __init__(self, mnemonic, password = '') -> None:
        self.mnemonic = mnemonic.strip()
        self.password = password 
    
    def get_address_bip44(self):
        seed_bytes = Bip39SeedGenerator(self.mnemonic).Generate(self.password)
        bip44_mst_ctx = Bip44.FromSeed(seed_bytes, Bip44Coins.BITCOIN).Purpose().Coin().Account(0).Change(Bip44Changes.CHAIN_EXT).AddressIndex(0)
        return {"address" : bip44_mst_ctx.PublicKey().ToAddress(),
                "private" : f"{bip44_mst_ctx.PrivateKey().ToWif()}"}
        
    def get_address_bip49(self):
        seed_bytes = Bip39SeedGenerator(self.mnemonic).Generate(self.password)
        bip44_mst_ctx = Bip49.FromSeed(seed_bytes, Bip49Coins.BITCOIN).Purpose().Coin().Account(0).Change(Bip44Changes.CHAIN_EXT).AddressIndex(0)
        return {"address" : bip44_mst_ctx.PublicKey().ToAddress(),
                "private" : f"{bip44_mst_ctx.PrivateKey().ToWif()}"}
    
    def get_address_bip84(self):
        seed_bytes = Bip39SeedGenerator(self.mnemonic).Generate(self.password)
        bip44_mst_ctx = Bip84.FromSeed(seed_bytes, Bip84Coins.BITCOIN).Purpose().Coin().Account(0).Change(Bip44Changes.CHAIN_EXT).AddressIndex(0)
        return {"address" : bip44_mst_ctx.PublicKey().ToAddress(),
                "private" : f"{bip44_mst_ctx.PrivateKey().ToWif()}"}
        
    
def generate(count: int = None, chain : str = "ETH", bip = None):
    if count == None:
        logger.info(f"Вы не указали количество генераций, будет сделано пять")
        count = 5
    date = {'mnemonic': [],
            'private': [],
            'address': []
            }

    mnemonics=[]
    for i in range(count):
        mnemonics.append(Mnemonic().generate())

    if chain == "SOL":
        for mnemonic in mnemonics:
            try:
                keys = SOLANA(mnemonic=mnemonic)
                info = keys.get_address(count)
                date["mnemonic"].append(mnemonic)
                date["private"].append(info["private"])
                date["address"].append(info["address"])
            except:
                continue
    elif chain == "APTOS":
        for mnemonic in mnemonics:
            try:
                keys = BTC(mnemonic=mnemonic, coin_type=Bip44Coins.APTOS)
                info = keys.get_address()
                date["mnemonic"].append(mnemonic)
                date["private"].append(info["private"])
                date["address"].append(info["address"])
            except:
                continue
    elif chain == "BTC":
        if bip == "BIP44":
            for mnemonic in mnemonics:
                try:
                    keys = BTC(mnemonic=mnemonic)
                    info = keys.get_address_bip44()
                    date["mnemonic"].append(mnemonic)
                    date["private"].append(info["private"])
                    date["address"].append(info["address"])
                except:
                    continue
        elif bip == "BIP49":
            for mnemonic in mnemonics:
                try:
                    keys = BTC(mnemonic=mnemonic)
                    info = keys.get_address_bip49()
                    date["mnemonic"].append(mnemonic)
                    date["private"].append(info["private"])
                    date["address"].append(info["address"])
                except:
                    continue
        elif bip == "BIP84":
            for mnemonic in mnemonics:
                try:
                    keys = BTC(mnemonic=mnemonic)
                    info = keys.get_address_bip84()
                    date["mnemonic"].append(mnemonic)
                    date["private"].append(info["private"])
                    date["address"].append(info["address"])
                except:
                    continue
    else:
        for mnemonic in mnemonics:
            try:
                keys = EVM(mnemonic=mnemonic)
                info = keys.get_address()
                date["mnemonic"].append(mnemonic)
                date["private"].append(info["private"])
                date["address"].append(info["address"])
            except:
                continue
        
            
    writer = pd.ExcelWriter('./wallets.xlsx') 
    df = pd.DataFrame(date)
    df.to_excel(writer, sheet_name='wallets', index=False, na_rep='NaN')

    for column in df:
        column_length = max(df[column].astype(str).map(len).max(), len(column))
        col_idx = df.columns.get_loc(column)
        writer.sheets['wallets'].set_column(col_idx, col_idx, column_length)
    writer._save()
    
    if os.name == "posix":
        path = f"{os.getcwd()}/wallets.xlsx"
    elif os.name == "nt":
        path = f"{os.getcwd()}\wallets.xlsx"
    else:
        path = f"wallets.xlsx"
        logger.success(f"ГЕНЕРАЦИЯ ЗАВЕРШЕНА, проверьте файл {path} в вашей директории")
    logger.success(f"ГЕНЕРАЦИЯ ЗАВЕРШЕНА, проверьте файл {path}")
