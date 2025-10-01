import os
import requests
import time
from datetime import datetime
import sys

# 🚀 مصادر API المتنوعة
SOLANA_DEX_ID = "solana"
SEARCH_API_URL = "https://api.dexscreener.com/latest/dex/search"
TRENDING_API_URL = "https://api.dexscreener.com/latest/dex/search/trending" 

print(f"🚀 بدء تشغيل بوت الترندينغ الحقيقي - الإصدار V6.4 (استراتيجية التنويع العكسي)")

class RealDEXTrendingBot:
    def __init__(self, telegram_token, channel_id):
        self.telegram_token = telegram_token
        self.channel_id = channel_id
        self.last_sent_tokens = set() 
        print("✅ تم تهيئة البوت الحقيقي!")

    def fetch_data_from_api(self, url, params=None, source_name="API"):
        """دالة مساعدة لجلب البيانات بتسامح مع الأخطاء"""
        headers = {
            # استخدام User-Agent قياسي لمحاولة تجاوز بعض الحظر
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'application/json',
            'Referer': 'https://dexscreener.com/',
        }
        try:
            print(f"🔄 محاولة جلب البيانات من {source_name}...")
            response = requests.get(url, headers=headers, params=params, timeout=20)
            
            if response.status_code != 200:
                print(f"❌ خطأ في {source_name} ({response.status_code}): تعذر جلب البيانات. (سيتم المحاولة في مصدر آخر)")
                return None
            
            data = response.json()
            pairs = data.get('pairs')
            
            if not isinstance(pairs, list):
                print(f"❌ تنسيق الأزواج غير صالح أو مفقود في {source_name}: {type(pairs)}. (سيتم المحاولة في مصدر آخر)")
                return [] 
                
            print(f"✅ نجح الجلب من {source_name}. عدد الأزواج: {len(pairs)}")
            return pairs
            
        except Exception as e:
            print(f"❌ خطأ غير متوقع في جلب البيانات من {source_name}: {e}. (سيتم المحاولة في مصدر آخر)")
            return None

    def get_multi_source_data(self):
        """تنويع مصادر الجلب بين البحث (أساسي) والترندينغ (احتياطي)"""
        
        # 1. 🔍 المحاولة الأولى: API البحث
        search_pairs = self.fetch_data_from_api(
            SEARCH_API_URL, 
            params={'q': 'raydium', 'limit': 75}, 
            source_name="API البحث"
        )
        
        if search_pairs is not None and isinstance(search_pairs, list) and search_pairs:
            # ترتيب الأزواج حسب تاريخ الإنشاء لتحديد الترند (البحث يعيد بيانات غير مرتبة)
            search_pairs.sort(key=lambda p: p.get('pairCreatedAt', 0), reverse=True)
            return search_pairs

        # 2. ⚡️ المحاولة الثانية: API الترندينغ
        trending_pairs = self.fetch_data_from_api(
            TRENDING_API_URL, 
            params={'limit': 75}, 
            source_name="API الترندينغ"
        )
        
        if trending_pairs is not None and isinstance(trending_pairs, list):
            return trending_pairs

        print("❌ فشلت كل محاولات الجلب. إعادة قائمة فارغة.")
        return []

    def filter_solana_tokens(self, pairs):
        """تصفية عملات Solana فقط والتحقق من البيانات الأساسية"""
        if not pairs: return []
        
        solana_pairs = []
        for pair in pairs:
            if pair and isinstance(pair, dict) and pair.get('chainId') == SOLANA_DEX_ID:
                liquidity_data = pair.get('liquidity', {})
                liquidity_usd = liquidity_data.get('usd', 0)
                pair_address = pair.get('pairAddress')
                
                # شرط بسيط للتصفية: سيولة أكبر من صفر ووجود عنوان
                if liquidity_usd > 0 and pair_address:
                    solana_pairs.append(pair)
            
        print(f"🔍 تم تصفية {len(solana_pairs)} عملة Solana.")
        return solana_pairs

    # 🌟 شروط صارمة (25K سيولة، 5% 5M، 30 دقيقة عمر) - هذا هو ما يجب أن ينطبق
    def check_token_conditions(self, token):
        """فحص الشروط للتركيز على العملات النشطة"""
        try:
            # 1. فحص السيولة الحقيقية 
            liquidity_data = token.get('liquidity', {})
            liquidity = liquidity_data.get('usd', 0)
            MIN_LIQUIDITY = 25000 
            if liquidity < MIN_LIQUIDITY: return False
            
            # 2. فحص الأداء في 5 دقائق 
            price_change = token.get('priceChange', {})
            change_5m = price_change.get('m5', 0)
            MIN_5M_CHANGE = 5.0 
            if change_5m < MIN_5M_CHANGE: return False
            
            # 3. فحص العمر الحقيقي - لا يتجاوز 30 دقيقة
            pair_created_at = token.get('pairCreatedAt')
            MAX_AGE_MINUTES = 30  
            if pair_created_at:
                age_minutes = (time.time() - pair_created_at/1000) / 60
                if age_minutes > MAX_AGE_MINUTES: return False
            else:
                return False
            
            # 4. فحص حجم التداول (Volume) - (50K)
            volume_data = token.get('volume', {})
            volume_24h = volume_data.get('h24', 0)
            MIN_VOLUME_24H = 50000 
            if volume_24h < MIN_VOLUME_24H: return False
            
            return True
            
        except Exception as e:
            return False
    
    # ... (بقية الدوال analyze_real_token, format_real_token_message, send_telegram_message لم تتغير)
    def analyze_real_token(self, token):
        try:
            if not token or not isinstance(token, dict): return None
            # ... (كود التحليل وتحديد قوة الإشارة هنا - لم يتغير)
            base_token = token.get('baseToken', {})
            symbol = base_token.get('symbol', 'Unknown')
            name = base_token.get('name', 'Unknown')
            price = float(token.get('priceUsd', 0.001))
            liquidity = float(token.get('liquidity', {}).get('usd', 10000))
            market_cap = float(token.get('marketCap', liquidity * 2))
            volume_24h = float(token.get('volume', {}).get('h24', liquidity * 0.3))
            change_5m = float(token.get('priceChange', {}).get('m5', 0))
            change_1h = float(token.get('priceChange', {}).get('h1', 0))
            pair_address = token.get('pairAddress', '')
            base_token_address = base_token.get('address', '')
            dex_id = token.get('dexId', 'Unknown')
            url = token.get('url', f"https://dexscreener.com/solana/{pair_address}")
            
            pair_created_at = token.get('pairCreatedAt')
            if pair_created_at:
                age_minutes = (time.time() - pair_created_at/1000) / 60
                age_text = f"{age_minutes:.0f} دقيقة" if age_minutes < 60 else f"{age_minutes / 60:.1f} ساعة"
            else:
                age_text = "غير معروف"
                
            short_pair_address = pair_address[:8] + "..." + pair_address[-6:]
            short_token_address = base_token_address[:8] + "..." + base_token_address[-6:]
            
            signal_score = 0
            if liquidity > 500000: signal_score += 4  
            elif liquidity > 100000: signal_score += 2
            elif liquidity > 25000: signal_score += 1
            if volume_24h > 1000000: signal_score += 2 
            elif volume_24h > 500000: signal_score += 1
            if change_5m > 25: signal_score += 3 
            elif change_5m > 10: signal_score += 2
            elif change_5m > 5: signal_score += 1 
            if change_1h > 80: signal_score += 4 
            elif change_1h > 40: signal_score += 2
            
            if signal_score >= 10:
                signal = "🚀 صاروخي | ترند عالي الجودة"
                emoji = "🚀"
                urgency = "🔥 عاجل جداً"
            elif signal_score >= 6:
                signal = "📈 قوي جداً | دخول ترند"
                emoji = "📈"
                urgency = "⚡ عاجل"
            elif signal_score >= 3:
                signal = "🔥 ممتاز | زخم إيجابي"
                emoji = "🔥"
                urgency = "📊 جيد"
            else:
                return None 
            
            token_id = f"solana_{pair_address}"
            
            return {
                'symbol': symbol, 'name': name, 'price': price, 'liquidity': liquidity,
                'market_cap': market_cap, 'volume_24h': volume_24h, 'change_5m': change_5m,
                'change_1h': change_1h, 'age': age_text, 'signal': signal, 'emoji': emoji,
                'urgency': urgency, 'pair_address': short_pair_address, 'token_address': short_token_address,
                'full_pair_address': pair_address, 'url': url, 'exchange': dex_id, 'token_id': token_id
            }
        except Exception as e:
            return None
    
    def format_real_token_message(self, token_analysis):
        try:
            if not token_analysis: return None
            # ... (كود تنسيق الرسالة هنا - لم يتغير)
            price = token_analysis['price']
            if price < 0.000001: price_text = f"${price:.8f}"
            elif price < 0.0001: price_text = f"${price:.6f}"
            elif price < 0.01: price_text = f"${price:.4f}"
            else: price_text = f"${price:.4f}"
            
            def format_currency(value):
                if value == 0: return "$0"
                elif value >= 1000000: return f"${value/1000000:.2f}M"
                elif value >= 1000: return f"${value/1000:.1f}K"
                else: return f"${value:.0f}"
            
            market_cap_text = format_currency(token_analysis['market_cap'])
            liquidity_text = format_currency(token_analysis['liquidity'])
            volume_text = format_currency(token_analysis['volume_24h'])
            pooled_sol = token_analysis['liquidity'] / 100  
            tokens_per_sol = int(1/price) if price > 0 else 0
            
            message = f"""
{token_analysis['emoji']} **{token_analysis['urgency']} | {token_analysis['name']} (${token_analysis['symbol']})**

🎯 **الإشارة:** {token_analysis['signal']}
⏰ **العمر:** {token_analysis['age']}
🔗 **المنصة:** {token_analysis['exchange']}

🪅 **عنوان العقدة:**
`{token_analysis['token_address']}`

⛽️ **عنوان التبادل (Pair):**
`{token_analysis['pair_address']}`

📊 **البيانات المالية:**
• **القيمة السوقية:** {market_cap_text}
• **السيولة (Liquidity):** {liquidity_text}
• **الحجم (24h Volume):** {volume_text}
• **السعر:** {price_text}
• **SOL المربوطة:** {pooled_sol:.0f} SOL

📈 **الأداء الفعلي:**
• **5 دقائق:** {token_analysis['change_5m']:+.1f}%
• **ساعة:** {token_analysis['change_1h']:+.1f}%

⚖️ **1 SOL تقريباً = {tokens_per_sol:,} {token_analysis['symbol']}**

🔍 **الروابط:**
[عرض على DEXScreener]({token_analysis['url']})
[تداول على {token_analysis['exchange']}]({token_analysis['url']})

🕒 **{datetime.now().strftime('%I:%M %p')}** ✅
💎 **بيانات حية ومباشرة (V6.4)**
"""
            return message
        except Exception as e:
            return None

    def send_telegram_message(self, message):
        """إرسال رسالة إلى Telegram"""
        try:
            if not message: return False
                
            url = f"https://api.telegram.org/bot{self.telegram_token}/sendMessage"
            payload = {
                'chat_id': self.channel_id,
                'text': message,
                'parse_mode': 'Markdown',
                'disable_web_page_preview': False
            }
            
            response = requests.post(url, json=payload, timeout=10)
            if response.status_code == 200: return True
            else: return False
                
        except Exception as e:
            return False
    
    def run_real_analysis(self):
        """تشغيل التحليل بالبيانات الحقيقية"""
        
        all_pairs = self.get_multi_source_data() 
        
        if not all_pairs:
            error_message = f"""
❌ **تعذر جلب بيانات الترندينغ الحية من أي API موثوق به**

⏰ {datetime.now().strftime('%I:%M %p')}
⚠️ توقف البوت: فشل جلب البيانات من المصدرين (البحث والترندينغ).
"""
            self.send_telegram_message(error_message)
            return 0
        
        solana_pairs = self.filter_solana_tokens(all_pairs)
        
        # ... (بقية كود تشغيل التحليل والإرسال - لم يتغير)
        if not solana_pairs: return 0
        
        qualified_tokens = [token for token in solana_pairs if self.check_token_conditions(token)]
        analyzed_tokens = [self.analyze_real_token(token) for token in qualified_tokens]
        analyzed_tokens = [a for a in analyzed_tokens if a]

        if analyzed_tokens:
            analyzed_tokens.sort(key=lambda x: x.get('change_5m', 0) * x.get('liquidity', 0), reverse=True) 
            if len(analyzed_tokens) > 4: analyzed_tokens = analyzed_tokens[:4]

        if not analyzed_tokens:
            no_tokens_message = f"""
📭 **لا توجد عملات ترند قوية حاليًا**

✅ تم فحص {len(solana_pairs)} عملة، ولكن لم تستوفِ أي منها شروط الجودة الصارمة.
⏰ {datetime.now().strftime('%I:%M %p')}
🔄 جاري البحث عن عملات جديدة...
"""
            self.send_telegram_message(no_tokens_message)
            return 0
        
        successful_sends = 0
        for analysis in analyzed_tokens:
            message = self.format_real_token_message(analysis)
            token_unique_id = analysis.get('full_pair_address', analysis['token_id']) 
            
            if message and token_unique_id not in self.last_sent_tokens:
                if self.send_telegram_message(message):
                    successful_sends += 1
                    self.last_sent_tokens.add(token_unique_id)
                    time.sleep(3) 
        
        self.send_real_summary(successful_sends, len(analyzed_tokens), len(solana_pairs))
        
        return successful_sends
    
    def send_real_summary(self, successful_sends, qualified_count, total_count):
        try:
            summary = f"""
📊 **ملخص التحديث - {datetime.now().strftime('%I:%M %p')}**

✅ تم إرسال **{successful_sends}** توصية جديدة 
🔍 من أصل **{qualified_count}** عملة مؤهلة
📈 من إجمالي **{total_count}** عملة تم فحصها

💎 **مصدر البيانات:** DEX Screener API متعدد (البحث/الترندينغ) (V6.4)
🔄 **التحديث القادم:** 5 دقائق
"""
            self.send_telegram_message(summary)
        except Exception as e:
            pass

# التشغيل الرئيسي
if __name__ == "__main__":
    TELEGRAM_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
    CHANNEL_ID = os.environ.get('TELEGRAM_CHANNEL_ID')
    
    if not TELEGRAM_TOKEN or not CHANNEL_ID:
        sys.exit(1)
    
    bot = RealDEXTrendingBot(TELEGRAM_TOKEN, CHANNEL_ID)
    
    try:
        start_message = f"""
🤖 **بدء بوت الترندينغ الحقيقي - الإصدار 6.4 (V6.4)**

⏰ {datetime.now().strftime('%Y-%m-%d %I:%M %p')}
🎯 **تحسينات الموثوقية الجذرية 3:** تم تفعيل استراتيجية **التنويع العكسي** لضمان الحصول على بيانات صالحة من أي مصدر ممكن.
🔄 التكرار: كل 5 دقائق
"""
        bot.send_telegram_message(start_message)
        
        count = bot.run_real_analysis()
        
    except Exception as e:
        try:
            error_msg = f"❌ خطأ فني في البوت: {str(e)[:200]}..."
            bot.send_telegram_message(error_msg)
        except:
            pass
    
    sys.exit(0)
