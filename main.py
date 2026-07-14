"""
Telegram Global Search Bot
Kullanım: python main.py
"""

import os
from telethon import TelegramClient
from telethon.tl.functions.messages import SearchGlobalRequest
from telethon.tl.types import InputMessagesFilterEmpty
import asyncio

# ==================== AYARLAR ====================
API_ID = int(os.getenv('API_ID', 'YOUR_API_ID'))
API_HASH = os.getenv('API_HASH', 'YOUR_API_HASH')
SESSION_NAME = 'telegram_search'

# Kanal başına max sonuç
MAX_RESULTS_PER_CHANNEL = 100
# Genel max sonuç
TOTAL_MAX_RESULTS = 500
# ==================== AYARLAR ====================

client = TelegramClient(SESSION_NAME, API_ID, API_HASH)

async def search_telegram(query, limit=TOTAL_MAX_RESULTS):
    """Telegram'da kelime ara"""
    results = []
    
    print(f"🔍 '{query}' aranıyor...")
    
    async with client:
        # Global arama yap
        async for message in client.iter_messages(
            None,  # Tüm kaynaklarda ara
            search=query,
            filter=InputMessagesFilterEmpty(),
            limit=limit
        ):
            if message.chat:
                result = {
                    'id': message.id,
                    'date': message.date.strftime('%Y-%m-%d %H:%M') if message.date else 'N/A',
                    'chat_title': message.chat.title if hasattr(message.chat, 'title') else str(message.chat),
                    'chat_username': getattr(message.chat, 'username', None) or 'Özel',
                    'chat_id': message.chat.id,
                    'message': message.text[:500] if message.text else '[Medya/Görsel]',
                    'has_media': bool(message.media),
                    'media_type': type(message.media).__name__ if message.media else None,
                    'link': f"https://t.me/{message.chat.username}/{message.id}" if hasattr(message.chat, 'username') and message.chat.username else None
                }
                results.append(result)
                
                # Her 100 mesajda bilgi ver
                if len(results) % 100 == 0:
                    print(f"   📊 {len(results)} sonuç bulundu...")
    
    return results

def format_results(results, query):
    """Sonuçları güzel formatla"""
    output = []
    output.append(f"📊 Toplam: {len(results)} sonuç bulundu")
    output.append(f"🔍 Arama: {query}")
    output.append("=" * 50)
    
    # Sonuçları grupla
    channels = {}
    for r in results:
        ch = r['chat_title']
        if ch not in channels:
            channels[ch] = {
                'username': r['chat_username'],
                'count': 0,
                'messages': []
            }
        channels[ch]['count'] += 1
        channels[ch]['messages'].append(r)
    
    output.append(f"\n📢 {len(channels)} farklı kanal/grup")
    output.append("-" * 50)
    
    # En çok sonuç olan kanalları listele
    sorted_channels = sorted(channels.items(), key=lambda x: x[1]['count'], reverse=True)
    
    for i, (ch_name, ch_data) in enumerate(sorted_channels[:20], 1):
        username = f"@{ch_data['username']}" if ch_data['username'] else "🔒 Özel"
        output.append(f"\n{i}. 📢 {ch_name}")
        output.append(f"   👤 {username}")
        output.append(f"   💬 {ch_data['count']} mesaj")
        
        # İlk 3 mesajın önizlemesi
        for j, msg in enumerate(ch_data['messages'][:3], 1):
            text = msg['message'][:100] + "..." if len(msg['message']) > 100 else msg['message']
            media = "📎 " if msg['has_media'] else ""
            output.append(f"   {j}. {media}[{msg['date']}] {text}")
    
    return "\n".join(output)

async def main():
    print("=" * 50)
    print("🔍 TELEGRAM GLOBAL SEARCH BOT")
    print("=" * 50)
    print("\nÇıkmak için Ctrl+C basın\n")
    
    while True:
        query = input("Aramak istediğiniz kelime: ").strip()
        
        if not query:
            continue
        if query.lower() in ['çıkış', 'exit', 'quit']:
            print("👋 Görüşürüz!")
            break
        
        print()
        results = await search_telegram(query)
        
        if results:
            output = format_results(results, query)
            print("\n" + output)
            
            # Sonuçları dosyaya da kaydet
            filename = f"sonuclar_{query.replace(' ', '_')}.txt"
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(output)
            print(f"\n📁 Sonuçlar '{filename}' dosyasına kaydedildi")
        else:
            print("❌ Sonuç bulunamadı")
        
        print()

if __name__ == '__main__':
    print("\n📱 Telegram hesabınıza giriş yapılıyor...")
    print("   İlk çalıştırmada telefon numaranızı ve kodu girmeniz istenecek.\n")
    asyncio.run(main())
