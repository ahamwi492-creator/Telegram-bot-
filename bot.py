import os
import requests
import time
from datetime import datetime
import sys

# 🚀 استبدال API البحث بـ API أحدث الأزواج (New Pairs API) لزيادة الموثوقية
SOLANA_DEX_ID = "solana"
# استخدام API مخصص لأحدث الأزواج (New Pairs) وهو أكثر استقراراً
NEW_PAIRS_API_URL = f"https://api.dexscreener.com/latest/dex/pairs/{SOLANA_DEX_ID}" 

print(f"🚀 بدء تشغيل بوت الترندينغ الحقيقي - الإصدار V6.3 (استراتيجية أحدث الأزواج)")

class RealDEXTrendingBot:
    def __init__(self, telegram_token, channel_id):
        self.telegram_token = telegram_token
        self.channel_id = channel_id
        # نحتفظ بقائمة العملات المرسلة لمنع التكرار
        self.last_sent_tokens = set() 
        print("✅ تم تهيئة البوت الحقيقي!")

    def get_new_solana_pairs(self):
        """جلب أحدث أزواج Solana من API New Pairs (V6.3 Strategy)"""
        try:
            params = {
                # طلب عدد كبير من الأزواج الحديثة للفلترة
                'limit': 100 
            }
            
            print("🔄 جلب أحدث 100 زوج من Solana API...")
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'application/json',
                'Referer': 'https://dexscreener.com/',
            }
            
            response = requests.get(NEW_PAIRS_API_URL, headers=headers, params=params, timeout=20) 
            
            if response.status_code != 200:
                print(f"❌ خطأ في API أحدث الأزواج ({response.status_code}): تعذر جلب البيانات.")
                return []
            
            data = response.json()
            
            pairs = data.get('pairs')
            
            if not isinstance(pairs, list) or not pairs:
                print(f"❌ تنسيق الأزواج غير صالح أو مفقود. (Received type: {type(pairs)}). قد لا تتوفر أزواج جديدة حالياً.")
                return []
            
            print(f"✅ تم جلب البيانات بنجاح من API. عدد الأزواج المستلمة: {len(pairs)}")
            
            # API أحدث الأزواج يعيدها مرتبة حسب تاريخ الإنشاء تلقائياً
            return pairs
            
        except Exception as e:
            print(f"❌ خطأ غير متوقع في جلب البيانات: {e}")
            import traceback
            print(f"🔍 تفاصيل الخطأ: {traceback.format_exc()}")
            return []
    
    # دالة تصفية Solana والتحقق من البيانات الأساسية (لم تتغير)
    def filter_solana_tokens(self, pairs):
        """تصفية عملات Solana فقط والتحقق من البيانات الأساسية (السيولة/السعر/العقد)"""
        if not pairs:
            return []
        
        solana_pairs = []
        for pair in pairs:
            if pair and isinstance(pair, dict) and pair.get('chainId') == SOLANA_DEX_ID:
                
                liquidity_data = pair.get('liquidity', {})
                liquidity_usd = liquidity_data.get('usd') if isinstance(liquidity_data, dict) else None
                if liquidity_usd is None: liquidity_usd = 0
                
                price_usd = pair.get('priceUsd')
                pair_address = pair.get('pairAddress')
                
                if liquidity_usd > 0 and price_usd is not None and pair_address:
                    solana_pairs.append(pair)
                else:
                    symbol = pair.get('baseToken', {}).get('symbol')
                    # هذا أمر طبيعي مع العملات الجديدة جداً
                    # print(f"   ⚠️ تجاهل عملة بدون سيولة/سعر/عنوان زوج: {symbol if symbol else 'Unknown'}")
                    pass
            
        print(f"🔍 تم تصفية {len(solana_pairs)} عملة Solana (بعد التحقق من البيانات الأساسية).")
        return solana_pairs

    # 🌟 شروط صارمة (تم تخفيف السيولة إلى 25K في V6.1)
    def check_token_conditions(self, token):
        """فحص الشروط للتركيز على العملات النشطة في آخر 5 دقائق (30 دقيقة حد أقصى للعمر)"""
        try:
            base_token = token.get('baseToken', {})
            symbol = base_token.get('symbol', 'Unknown')
            name = base_token.get('name', 'Unknown')
            
            print(f"\n🔍 فحص شروط (Trending 5M - 30m Age): {symbol} ({name})")
            
            # 1. فحص السيولة الحقيقية 
            liquidity_data = token.get('liquidity', {})
            liquidity = liquidity_data.get('usd', 0) if isinstance(liquidity_data, dict) else 0
            
            # الحد الأدنى للسيولة 25K (لزيادة مرونة العملات السريعة)
            MIN_LIQUIDITY = 25000 
            print(f"   💰 السيولة: ${liquidity:,.0f}")
            if liquidity < MIN_LIQUIDITY: 
                print(f"   ❌ السيولة منخفضة (أقل من ${MIN_LIQUIDITY:,})")
                return False
            
            # 2. فحص الأداء في 5 دقائق (5.0%)
            price_change = token.get('priceChange', {})
            if not isinstance(price_change, dict):
                price_change = {}
                
            change_5m = price_change.get('m5', 0)
            
            print(f"   📈 الأداء: 5m={change_5m:.1f}%")
            
            MIN_5M_CHANGE = 5.0 
            if change_5m < MIN_5M_CHANGE:
                print(f"   ❌ ارتفاع 5 دقائق ضعيف (أقل من {MIN_5M_CHANGE}%)")
                return False
            
            # 3. فحص العمر الحقيقي - لا يتجاوز 30 دقيقة
            pair_created_at = token.get('pairCreatedAt')
            MAX_AGE_MINUTES = 30  
            if pair_created_at:
                age_minutes = (time.time() - pair_created_at/1000) / 60
                print(f"   ⏰ العمر: {age_minutes:.1f} دقيقة")
                
                if age_minutes > MAX_AGE_MINUTES: 
                    print(f"   ❌ العملة قديمة (أكبر من {MAX_AGE_MINUTES} دقيقة)")
                    return False
            else:
                print("   ⚠️ لا يوجد تاريخ إنشاء للزوج")
                return False
            
            # 4. فحص حجم التداول (Volume) - (50K)
            volume_data = token.get('volume', {})
            volume_24h = volume_data.get('h24', 0) if isinstance(volume_data, dict) else 0
            MIN_VOLUME_24H = 50000 
            print(f"   💰 حجم 24h: ${volume_24h:,.0f}")

            if volume_24h < MIN_VOLUME_24H: 
                print(f"   ❌ حجم التداول منخفض (أقل من ${MIN_VOLUME_24H:,})")
                return False
            
            print("   ✅ العملة مؤهلة للـ Trending 5M")
            return True
            
        except Exception as e:
            print(f"❌ خطأ في فحص الشروط: {e}")
            return False
    
    # ... (بقية الدالة analyze_real_token لم تتغير)
    def analyze_real_token(self, token):
        """تحليل العملة بناءً على البيانات الحقيقية وتحديد قوة الإشارة"""
        try:
            if not token or not isinstance(token, dict):
                return None
                
            base_token = token.get('baseToken', {})
            symbol = base_token.get('symbol', 'Unknown')
            name = base_token.get('name', 'Unknown')
            price = float(token.get('priceUsd', 0.001))
            
            liquidity_data = token.get('liquidity', {})
            liquidity = float(liquidity_data.get('usd', 10000)) if isinstance(liquidity_data, dict) else 10000
            
            market_cap = float(token.get('marketCap', liquidity * 2))
            
            volume_data = token.get('volume', {})
            volume_24h = float(volume_data.get('h24', liquidity * 0.3)) if isinstance(volume_data, dict) else liquidity * 0.3
            
            price_change = token.get('priceChange', {})
            change_5m = float(price_change.get('m5', 0))
            change_1h = float(price_change.get('h1', 0))
            
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
                
            short_pair_address = pair_address[:8] + "..." + pair_address[-6:] if len(pair_address) > 20 else pair_address
            short_token_address = base_token_address[:8] + "..." + base_token_address[-6:] if len(base_token_address) > 20 else base_token_address
            
            
            signal_score = 0
            
            # 1. تقييم الجودة (السيولة والحجم)
            if liquidity > 500000: signal_score += 4  
            elif liquidity > 100000: signal_score += 2
            elif liquidity > 25000: signal_score += 1
                
            if volume_24h > 1000000: signal_score += 2 
            elif volume_24h > 500000: signal_score += 1

            # 2. تقييم الزخم السعري
            if change_5m > 25: signal_score += 3 
            elif change_5m > 10: signal_score += 2
            elif change_5m > 5: signal_score += 1 
                
            if change_1h > 80: signal_score += 4 
            elif change_1h > 40: signal_score += 2
            
            # 3. تحديد الإشارة النهائية
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
            
            token_id = f"solana_{pair_address}" if pair_address else f"{symbol}_{int(time.time())}"
            
            return {
                'symbol': symbol,
                'name': name,
                'price': price,
                'liquidity': liquidity,
                'market_cap': market_cap,
                'volume_24h': volume_24h,
                'change_5m': change_5m,
                'change_1h': change_1h,
                'age': age_text,
                'signal': signal,
                'emoji': emoji,
                'urgency': urgency,
                'pair_address': short_pair_address,
                'token_address': short_token_address,
                'full_pair_address': pair_address,
                'full_token_address': base_token_address,
                'url': url,
                'exchange': dex_id,
                'token_id': token_id
            }
            
        except Exception as e:
            print(f"❌ خطأ في تحليل العملة: {e}")
            return None
    
    # ... (بقية الدالة format_real_token_message لم تتغير)
    def format_real_token_message(self, token_analysis):
        """تنسيق رسالة بناءً على البيانات الحقيقية"""
        try:
            if not token_analysis:
                return None
                
            price = token_analysis['price']
            if price < 0.000001:
                price_text = f"${price:.8f}"
            elif price < 0.0001:
                price_text = f"${price:.6f}"
            elif price < 0.01:
                price_text = f"${price:.4f}"
            else:
                price_text = f"${price:.4f}"
            
            def format_currency(value):
                if value == 0:
                    return "$0"
                elif value >= 1000000:
                    return f"${value/1000000:.2f}M"
                elif value >= 1000:
                    return f"${value/1000:.1f}K"
                else:
                    return f"${value:.0f}"
            
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
💎 **بيانات حية ومباشرة (V6.3)**
"""
            return message
            
        except Exception as e:
            print(f"❌ خطأ في تنسيق الرسالة: {e}")
            return None
    
    def send_telegram_message(self, message):
        """إرسال رسالة إلى Telegram"""
        try:
            if not message:
                return False
                
            url = f"https://api.telegram.org/bot{self.telegram_token}/sendMessage"
            payload = {
                'chat_id': self.channel_id,
                'text': message,
                'parse_mode': 'Markdown',
                'disable_web_page_preview': False
            }
            
            response = requests.post(url, json=payload, timeout=10)
            
            if response.status_code == 200:
                print("✅ تم إرسال الرسالة بنجاح")
                return True
            else:
                print(f"❌ فشل إرسال الرسالة: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ خطأ في الإرسال: {e}")
            return False
    
    def run_real_analysis(self):
        """تشغيل التحليل بالبيانات الحقيقية"""
        print("🔍 بدء التحليل بالبيانات الحية من API...")
        
        # 🎯 استخدام API أحدث الأزواج الموثوق به
        all_pairs = self.get_new_solana_pairs() 
        
        if not all_pairs:
            error_message = f"""
❌ **تعذر جلب بيانات الترندينغ الحية من API**

⏰ {datetime.now().strftime('%I:%M %p')}
⚠️ توقف البوت: فشل جلب بيانات أحدث الأزواج.
"""
            self.send_telegram_message(error_message)
            return 0
        
        solana_pairs = self.filter_solana_tokens(all_pairs)
        
        if not solana_pairs:
            print(f"⚠️ لم يتم العثور على عملات Solana مؤهلة بعد التحقق من {len(all_pairs)} زوج تم جلبه.")
            return 0
        
        print(f"📊 جاري تحليل {len(solana_pairs)} عملة جديدة...")
        
        qualified_tokens = []
        for token in solana_pairs:
            if self.check_token_conditions(token):
                qualified_tokens.append(token)
        
        print(f"🎯 العملات المؤهلة: {len(qualified_tokens)}")
        
        analyzed_tokens = []
        for token in qualified_tokens:
            analysis = self.analyze_real_token(token)
            if analysis:
                analyzed_tokens.append(analysis)
        
        if analyzed_tokens:
            # الترتيب حسب الزخم والقيمة لضمان إرسال الأفضل
            analyzed_tokens.sort(key=lambda x: x.get('change_5m', 0) * x.get('liquidity', 0), reverse=True) 
            
            if len(analyzed_tokens) > 4:
                analyzed_tokens = analyzed_tokens[:4]
                print(f"🎯 تم اختيار أفضل {len(analyzed_tokens)} عملة بناءً على التحليل")

        if not analyzed_tokens:
            no_tokens_message = f"""
📭 **لا توجد عملات ترند قوية حاليًا**

✅ تم فحص {len(solana_pairs)} عملة، ولكن لم تستوفِ أي منها شروط الجودة الصارمة (30 دقيقة و 5% 5M و 25K سيولة).
⏰ {datetime.now().strftime('%I:%M %p')}
🔄 جاري البحث عن عملات جديدة...
"""
            self.send_telegram_message(no_tokens_message)
            return 0
        
        successful_sends = 0
        for analysis in analyzed_tokens:
            message = self.format_real_token_message(analysis)
            token_unique_id = analysis.get('full_pair_address', analysis['token_id']) 
            
            # منع التكرار
            if message and token_unique_id not in self.last_sent_tokens:
                if self.send_telegram_message(message):
                    successful_sends += 1
                    self.last_sent_tokens.add(token_unique_id)
                    print(f"✅ تم إرسال توصية {analysis['symbol']}")
                    time.sleep(3) 
        
        self.send_real_summary(successful_sends, len(analyzed_tokens), len(solana_pairs))
        
        return successful_sends
    
    def send_real_summary(self, successful_sends, qualified_count, total_count):
        """إرسال ملخص بالبيانات الحقيقية"""
        try:
            summary = f"""
📊 **ملخص التحديث - {datetime.now().strftime('%I:%M %p')}**

✅ تم إرسال **{successful_sends}** توصية جديدة (بشروط جودة صارمة)
🔍 من أصل **{qualified_count}** عملة مؤهلة
📈 من إجمالي **{total_count}** عملة تم فحصها

💎 **مصدر البيانات:** DEX Screener API أحدث الأزواج (V6.3)
🎯 **التركيز:** عملات بعمر ≤ 30 دقيقة وارتفاع 5M ≥ 5.0% وسيولة ≥ 25K.
🔄 **التحديث القادم:** 5 دقائق
"""
            self.send_telegram_message(summary)
            
        except Exception as e:
            print(f"❌ خطأ في إرسال الملخص: {e}")

# التشغيل الرئيسي
if __name__ == "__main__":
    TELEGRAM_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
    CHANNEL_ID = os.environ.get('TELEGRAM_CHANNEL_ID')
    
    if not TELEGRAM_TOKEN or not CHANNEL_ID:
        print("❌ يرجى إضافة TELEGRAM_BOT_TOKEN و TELEGRAM_CHANNEL_ID في Secrets")
        sys.exit(1)
    
    bot = RealDEXTrendingBot(TELEGRAM_TOKEN, CHANNEL_ID)
    
    try:
        start_message = f"""
🤖 **بدء بوت الترندينغ الحقيقي - الإصدار 6.3 (V6.3)**

⏰ {datetime.now().strftime('%Y-%m-%d %I:%M %p')}
🎯 **تحسينات الموثوقية الجذرية 2:** تم تبديل مصدر البيانات إلى **API أحدث الأزواج** (`/pairs/solana`) لضمان الحصول على أحدث العملات بأكبر موثوقية وتجنب مشكلات API الترندينغ والبحث.
🔄 التكرار: كل 5 دقائق
"""
        bot.send_telegram_message(start_message)
        
        count = bot.run_real_analysis()
        print(f"✅ اكتمل التشغيل! تم إرسال {count} توصية")
        
    except Exception as e:
        print(f"❌ خطأ غير متوقع: {e}")
        import traceback
        print(f"🔍 تفاصيل الخطأ: {traceback.format_exc()}")
        
        try:
            error_msg = f"❌ خطأ فني في البوت: {str(e)[:200]}..."
            bot.send_telegram_message(error_msg)
        except:
            pass
    
    sys.exit(0)
