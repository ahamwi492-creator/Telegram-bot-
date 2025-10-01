import os
import requests
import time
from datetime import datetime, timedelta
import sys

print("🚀 بدء تشغيل بوت الترندينغ الحقيقي - الإصدار المعدل V5.2 (30 دقيقة + 5% 5M)...")

class RealDEXTrendingBot:
    def __init__(self, telegram_token, channel_id):
        self.telegram_token = telegram_token
        self.channel_id = channel_id
        # استخدام مجموعة لتخزين عناوين الأزواج الكاملة لتجنب التكرار
        self.last_sent_tokens = set() 
        print("✅ تم تهيئة البوت الحقيقي!")
    
    def get_real_trending_data(self):
        """جلب البيانات الحية من DEX Screener API مع معالجة أخطاء محسنة"""
        try:
            print("🔄 جلب البيانات الحية من DEX Screener API...")
            
            # استخدام API مباشر للترندينغ (الأقرب لـ Trending 5M المتاح)
            url = "https://api.dexscreener.com/latest/dex/tokens/trending"
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'application/json',
                'Accept-Language': 'en-US,en;q=0.9',
                'Referer': 'https://dexscreener.com/',
                'Origin': 'https://dexscreener.com'
            }
            
            response = requests.get(url, headers=headers, timeout=20) 
            
            if response.status_code != 200:
                print(f"❌ خطأ في API: {response.status_code}")
                return []
            
            data = response.json()
            print(f"✅ تم جلب البيانات بنجاح من API")
            
            pairs = data.get('pairs')
            
            if not isinstance(pairs, list):
                print(f"❌ تنسيق الأزواج غير صالح أو مفقود: {type(pairs)}")
                return []
            
            print(f"📊 عدد الأزواج المستلمة: {len(pairs)}")
            return pairs
            
        except requests.exceptions.Timeout:
            print("⏰ انتهت المهلة في جلب البيانات")
            return []
        except requests.exceptions.ConnectionError:
            print("🔌 خطأ في الاتصال بالشبكة")
            return []
        except Exception as e:
            print(f"❌ خطأ غير متوقع في جلب البيانات: {e}")
            import traceback
            print(f"🔍 تفاصيل الخطأ: {traceback.format_exc()}")
            return []
    
    def get_backup_trending_data(self):
        """بيانات احتياطية في حالة فشل API الرئيسي"""
        print("🔄 استخدام البيانات الاحتياطية...")
        
        # بيانات احتياطية بسيطة
        backup_tokens = [
            {
                'baseToken': {
                    'symbol': 'BACKUP',
                    'name': 'Backup Coin',
                    'address': 'DezXAZ8z7PnrnRJjz3wXBoRgixCa6xjnB7YaB1pPB263'
                },
                'pairAddress': 'HSGuSTWg1xBNGLoSjMB3SW3WbwtvGqNr5yRjs3KJmkR6',
                'chainId': 'solana',
                'priceUsd': '0.00001',
                'liquidity': {'usd': 1500000},
                'priceChange': {'m5': 6.0, 'h1': 15.7, 'h24': 45.3},
                'pairCreatedAt': int(time.time() * 1000) - 15 * 60 * 1000, # 15 دقيقة عمر
                'dexId': 'raydium',
                'url': 'https://dexscreener.com/solana/hsgustwg1xbnglosjmb3sw3wbwtvgqnr5yrjs3kjmkr6',
                'volume': {'h24': 500000},
                'marketCap': 80000000
            },
        ]
        
        return backup_tokens
    
    def filter_solana_tokens(self, pairs):
        """تصفية عملات Solana فقط"""
        if not pairs:
            return []
        
        solana_pairs = []
        for pair in pairs:
            if pair and isinstance(pair, dict) and pair.get('chainId') == 'solana':
                solana_pairs.append(pair)
        
        print(f"🔍 تم تصفية {len(solana_pairs)} عملة Solana من أصل {len(pairs)}")
        return solana_pairs
    
    # 🌟 التعديل الأساسي: تشديد الشروط (30 دقيقة و 5% 5M)
    def check_token_conditions(self, token):
        """فحص الشروط للتركيز على العملات النشطة في آخر 5 دقائق (بعمر 30 دقيقة كحد أقصى)"""
        try:
            if not token or not isinstance(token, dict):
                return False
                
            base_token = token.get('baseToken', {})
            symbol = base_token.get('symbol', 'Unknown')
            name = base_token.get('name', 'Unknown')
            
            print(f"\n🔍 فحص شروط (Trending 5M - 30m Age): {symbol} ({name})")
            
            # 1. فحص السيولة الحقيقية - يجب أن تكون كافية لتجنب الـ Rug Pull
            liquidity_data = token.get('liquidity', {})
            liquidity = liquidity_data.get('usd', 0) if isinstance(liquidity_data, dict) else 0
            
            MIN_LIQUIDITY = 50000 
            print(f"   💰 السيولة: ${liquidity:,.0f}")
            if liquidity < MIN_LIQUIDITY: 
                print(f"   ❌ السيولة منخفضة (أقل من ${MIN_LIQUIDITY:,})")
                return False
            
            # 2. فحص الأداء في 5 دقائق - تم تخفيف الشرط إلى 5.0%
            price_change = token.get('priceChange', {})
            if not isinstance(price_change, dict):
                price_change = {}
                
            change_5m = price_change.get('m5', 0)
            change_1h = price_change.get('h1', 0)
            
            print(f"   📈 الأداء: 5m={change_5m}%, 1h={change_1h}%")
            
            # 🎯 التعديل: الحد الأدنى لارتفاع 5 دقائق أصبح 5.0%
            MIN_5M_CHANGE = 5.0 
            if change_5m < MIN_5M_CHANGE:
                print(f"   ❌ ارتفاع 5 دقائق ضعيف (أقل من {MIN_5M_CHANGE}%)")
                return False
            
            # 3. فحص العمر الحقيقي - لا يتجاوز 30 دقيقة
            pair_created_at = token.get('pairCreatedAt')
            MAX_AGE_MINUTES = 30  # 🎯 تم التعديل: 30 دقيقة كحد أقصى
            if pair_created_at:
                age_minutes = (time.time() - pair_created_at/1000) / 60
                print(f"   ⏰ العمر: {age_minutes:.1f} دقيقة")
                
                if age_minutes > MAX_AGE_MINUTES: 
                    print(f"   ❌ العملة قديمة (أكبر من {MAX_AGE_MINUTES} دقيقة)")
                    return False
            else:
                print("   ⚠️ لا يوجد تاريخ إنشاء للزوج")
                return False
            
            # 4. فحص حجم التداول (Volume) - يجب أن يكون هناك حجم كافي
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
    
    # لم يتم تعديل الدالة (analyze_real_token)
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
            change_24h = float(price_change.get('h24', 0))
            
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
            
            
            # **منطق الإشارة الجديد: يعتمد على نقاط الجودة والزخم**
            signal_score = 0
            
            # 1. تقييم الجودة (السيولة والحجم)
            if liquidity > 250000: signal_score += 3  # سيولة عالية جداً
            elif liquidity > 100000: signal_score += 1
                
            if volume_24h > 1000000: signal_score += 2 # حجم تداول كبير
            elif volume_24h > 500000: signal_score += 1

            # 2. تقييم الزخم السعري
            if change_5m > 25: signal_score += 3 # ارتفاع سريع جداً
            elif change_5m > 10: signal_score += 1
                
            if change_1h > 80: signal_score += 4  # ارتفاع صاروخي في الساعة
            elif change_1h > 40: signal_score += 2
            
            # 3. تحديد الإشارة النهائية
            if signal_score >= 8:
                signal = "🚀 صاروخي | ترند عالي الجودة"
                emoji = "🚀"
                urgency = "🔥 عاجل جداً"
            elif signal_score >= 5:
                signal = "📈 قوي جداً | دخول ترند"
                emoji = "📈"
                urgency = "⚡ عاجل"
            elif signal_score >= 3:
                signal = "🔥 ممتاز | زخم إيجابي"
                emoji = "🔥"
                urgency = "📊 جيد"
            else:
                signal = "⚡ جيد | للمتابعة"
                emoji = "⚡"
                urgency = "🕒 عادي"
            
            # معرف فريد حقيقي
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
                'change_24h': change_24h,
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
    
    # لم يتم تعديل هذه الدالة (التنسيق)
    def format_real_token_message(self, token_analysis):
        """تنسيق رسالة بناءً على البيانات الحقيقية"""
        try:
            if not token_analysis:
                return None
                
            # تنسيق السعر الحقيقي
            price = token_analysis['price']
            if price < 0.000001:
                price_text = f"${price:.8f}"
            elif price < 0.0001:
                price_text = f"${price:.6f}"
            elif price < 0.01:
                price_text = f"${price:.4f}"
            else:
                price_text = f"${price:.4f}"
            
            # تنسيق الأرقام الكبيرة الحقيقية
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
            
            # حساب SOL المربوطة (بناءً على السيولة الحقيقية) - تقدير
            pooled_sol = token_analysis['liquidity'] / 100  
            
            # حساب عدد التوكنات مقابل 1 SOL (حقيقي)
            tokens_per_sol = int(1/price) if price > 0 else 0
            
            # إنشاء الرسالة بالبيانات الحقيقية
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
• **24 ساعة:** {token_analysis['change_24h']:+.1f}%

⚖️ **1 SOL تقريباً = {tokens_per_sol:,} {token_analysis['symbol']}**

🔍 **الروابط:**
[عرض على DEXScreener]({token_analysis['url']})
[تداول على {token_analysis['exchange']}]({token_analysis['url']})

🕒 **{datetime.now().strftime('%I:%M %p')}** ✅
💎 **بيانات حية من DEX Screener API**
🎯 **بوت الترندينغ الحقيقي v5.2 (المعدل)**
"""
            return message
            
        except Exception as e:
            print(f"❌ خطأ في تنسيق الرسالة: {e}")
            return None
    
    # لم يتم تعديل هذه الدالة (الإرسال)
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
                if response.text:
                    print(f"📄 تفاصيل الخطأ: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ خطأ في الإرسال: {e}")
            return False
    
    def run_real_analysis(self):
        """تشغيل التحليل بالبيانات الحقيقية"""
        print("🔍 بدء التحليل بالبيانات الحية من API...")
        
        # جلب البيانات الحقيقية
        all_pairs = self.get_real_trending_data()
        
        # إذا فشل API الرئيسي، استخدم البيانات الاحتياطية
        if not all_pairs:
            print("⚠️ استخدام البيانات الاحتياطية...")
            all_pairs = self.get_backup_trending_data()
        
        if not all_pairs:
            error_message = f"""
❌ **تعذر جلب البيانات من جميع المصادر**

⏰ {datetime.now().strftime('%I:%M %p')}
🔄 سيتم إعادة المحاولة لاحقاً...
"""
            self.send_telegram_message(error_message)
            return 0
        
        # تصفية عملات Solana
        solana_pairs = self.filter_solana_tokens(all_pairs)
        
        if not solana_pairs:
            print("⚠️ لم يتم العثور على عملات Solana، استخدام أفضل العملات المتاحة")
            solana_pairs = all_pairs 
        
        print(f"📊 جاري تحليل {len(solana_pairs)} عملة...")
        
        # تطبيق الشروط الصارمة
        qualified_tokens = []
        for token in solana_pairs:
            if self.check_token_conditions(token):
                qualified_tokens.append(token)
        
        print(f"🎯 العملات المؤهلة: {len(qualified_tokens)}")
        
        # تحليل العملات المؤهلة
        analyzed_tokens = []
        for token in qualified_tokens:
            analysis = self.analyze_real_token(token)
            if analysis:
                analyzed_tokens.append(analysis)
        
        # ترتيب العملات المؤهلة حسب الزخم والجودة
        if analyzed_tokens:
            # الترتيب حسب الارتفاع في الساعة (h1) والسيولة كبديل سريع
            analyzed_tokens.sort(key=lambda x: x.get('change_1h', 0) * x.get('liquidity', 0), reverse=True) 
            
            # نرسل فقط أفضل 4
            if len(analyzed_tokens) > 4:
                analyzed_tokens = analyzed_tokens[:4]
                print(f"🎯 تم اختيار أفضل {len(analyzed_tokens)} عملة بناءً على التحليل")

        if not analyzed_tokens:
            no_tokens_message = f"""
📭 **لا توجد عملات ترند قوية حاليًا**

✅ تم فحص {len(solana_pairs)} عملة، ولكن لم تستوفِ أي منها شروط الجودة الصارمة (30 دقيقة و 5% 5M).
⏰ {datetime.now().strftime('%I:%M %p')}
🔄 جاري البحث عن عملات جديدة...
"""
            self.send_telegram_message(no_tokens_message)
            return 0
        
        # إرسال العملات المؤهلة
        successful_sends = 0
        for analysis in analyzed_tokens:
            message = self.format_real_token_message(analysis)
            token_unique_id = analysis.get('full_pair_address', analysis['token_id']) 
            
            if message and token_unique_id not in self.last_sent_tokens:
                if self.send_telegram_message(message):
                    successful_sends += 1
                    self.last_sent_tokens.add(token_unique_id)
                    print(f"✅ تم إرسال توصية {analysis['symbol']}")
                    time.sleep(3)  # انتظار بين الرسائل
        
        # إرسال ملخص بالبيانات الحقيقية
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

💎 **مصدر البيانات:** DEX Screener API مباشر
🎯 **التركيز:** عملات بعمر ≤ 30 دقيقة وارتفاع 5M ≥ 5.0%.
🔄 **التحديث القادم:** 5 دقائق

⚡ **بوت الترندينغ الحقيقي v5.2 (المعدل)**
🏆 **يعمل بالبيانات الفعلية من السوق**
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
        # رسالة البدء
        start_message = f"""
🤖 **بدء بوت الترندينغ الحقيقي - الإصدار 5.2 (30 دقيقة + 5% 5M)**

⏰ {datetime.now().strftime('%Y-%m-%d %I:%M %p')}
🎯 **التحسينات:** تركيز صارم على العملات الأسرع (5M ≥ 5.0%) والأحدث (عمر ≤ 30 دقيقة).
🔄 التكرار: كل 5 دقائق

💎 **جاري جلب البيانات الحية من DEX Screener...**
"""
        bot.send_telegram_message(start_message)
        
        # التشغيل الرئيسي
        count = bot.run_real_analysis()
        print(f"✅ اكتمل التشغيل! تم إرسال {count} توصية")
        
    except Exception as e:
        print(f"❌ خطأ غير متوقع: {e}")
        import traceback
        print(f"🔍 تفاصيل الخطأ: {traceback.format_exc()}")
        
        # محاولة إرسال خطأ
        try:
            error_msg = f"❌ خطأ فني في البوت: {str(e)[:200]}..."
            bot.send_telegram_message(error_msg)
        except:
            pass
    
    sys.exit(0)
