import discord
from discord.ext import commands
import asyncio
from solana.rpc.async_api import AsyncClient
from solana.transaction import Transaction
from solana.keypair import Keypair
from solana.system_program import TransferParams, transfer
from spl.token.instructions import get_associated_token_account, create_associated_token_account
import json

# Bot configuration
TOKEN = 'YOUR_DISCORD_BOT_TOKEN'
CHANNELS_TO_MONITOR = [1292873731881832449]  # Replace with your channel IDs
KEYWORDS = ['buy', 'moon', 'pump']  # Add your trigger keywords

# Solana configuration
SOLANA_RPC_URL = "https://api.mainnet-beta.solana.com"
WALLET_PRIVATE_KEY = bytes([YOUR_PRIVATE_KEY_BYTES])  # Replace with your wallet private key
TOKEN_MINT_ADDRESS = "TOKEN_MINT_ADDRESS"  # Replace with the token's mint address
SOL_AMOUNT = 0.1

# Initialize bot
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

# Initialize Solana client
async_client = AsyncClient(SOLANA_RPC_URL)

async def buy_token(amount_sol):
    try:
        # Create keypair from private key
        keypair = Keypair.from_secret_key(WALLET_PRIVATE_KEY)
        
        # Get associated token account
        ata = await get_associated_token_account(
            TOKEN_MINT_ADDRESS,
            keypair.public_key
        )
        
        # If ATA doesn't exist, create it
        if not ata:
            create_ata_ix = create_associated_token_account(
                payer=keypair.public_key,
                owner=keypair.public_key,
                mint=TOKEN_MINT_ADDRESS
            )
            transaction = Transaction().add(create_ata_ix)
            await async_client.send_transaction(transaction, keypair)
        
        # Create transfer instruction
        transfer_ix = transfer(
            TransferParams(
                from_pubkey=keypair.public_key,
                to_pubkey=TOKEN_MINT_ADDRESS,
                lamports=int(amount_sol * 1e9)  # Convert SOL to lamports
            )
        )
        
        # Build and send transaction
        transaction = Transaction().add(transfer_ix)
        result = await async_client.send_transaction(transaction, keypair)
        return result['result']
    
    except Exception as e:
        print(f"Error during token purchase: {str(e)}")
        return None

@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')

@bot.event
async def on_message(message):
    # Check if message is from monitored channels
    if message.channel.id in CHANNELS_TO_MONITOR:
        # Check if message contains any keywords
        if any(keyword.lower() in message.content.lower() for keyword in KEYWORDS):
            print(f"Keyword detected in message: {message.content}")
            
            # Execute buy order
            tx_signature = await buy_token(SOL_AMOUNT)
            
            if tx_signature:
                print(f"Successfully purchased tokens. Transaction signature: {tx_signature}")
            else:
                print("Failed to purchase tokens")

    await bot.process_commands(message)

# Run the bot
bot.run(TOKEN)
