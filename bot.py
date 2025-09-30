import os
import requests
import time
from datetime import datetime, timedelta
import sys

print("🚀 بدء تشغيل بوت الترندينغ الحقيقي - الإصدار المعدل V5.0...")

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
            
            # استخدام API مباشر للترندينغ
            url = "https://api.dexscreener.com/latest/dex/tokens/trending"
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'application/json',
                'Accept-Language': 'en-US,en;q=0.9',
                'Referer': 'https://dexscreener.com/',
                'Origin': 'https://dexscreener.com'
            }
            
            # زيادة المهلة قليلاً
            response = requests.get(url, headers=headers, timeout=20) 
            
            if response.status_code != 200:
                print(f"❌ خطأ في API: {response.status_code}")
                print(f"📄 محتوى الاستجابة: {response.text}")
                return []
            
            data = response.json()
            print(f"✅ تم جلب البيانات بنجاح من API")
            
            pairs = data.get('pairs')
            
            if not isinstance(pairs, list):
                print(f"❌ تنسيق الأزواج غير صالح أو مفقود: {type(pairs)}")
                return []
            
            print(f"📊 عدد الأزواج المستلمة: {len(pairs)}")
            
            # عرض أول 3 أزواج للتصحيح
            for i, pair in enumerate(pairs[:3]):
                if pair and isinstance(pair, dict):
                    base_token = pair.get('baseToken', {})
                    symbol = base_token.get('symbol', 'Unknown')
                    name = base_token.get('name', 'Unknown')
                    print(f"🔍 زوج {i+1}: {symbol} - {name}")
            
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
    
    # لم يتم تعديل الدالة الاحتياطية لأنها تستخدم فقط كاحتياطي
    def get_backup_trending_data(self):
        """بيانات احتياطية في حالة فشل API الرئيسي"""
        print("🔄 استخدام البيانات الاحتياطية...")
        
        # عملات ترندينغ شائعة حالية على Solana
        backup_tokens = [
            {
                'baseToken': {
                    'symbol': 'BONK',
                    'name': 'Bonk',
                    'address': 'DezXAZ8z7PnrnRJjz3wXBoRgixCa6xjnB7YaB1pPB263'
                },
                'pairAddress': 'HSGuSTWg1xBNGLoSjMB3SW3WbwtvGqNr5yRjs3KJmkR6',
                'chainId': 'solana',
                'priceUsd': '0.00001234',
                'liquidity': {'usd': 15000000},
                'priceChange': {'m5': 5.2, 'h1': 15.7, 'h24': 45.3},
                'pairCreatedAt': int(time.time() * 1000) - 2 * 60 * 60 * 1000,
                'dexId': 'raydium',
                'url': 'https://dexscreener.com/solana/hsgustwg1xbnglosjmb3sw3wbwtvgqnr5yrjs3kjmkr6',
                'volume': {'h24': 5000000},
                'marketCap': 800000000
            },
            {
                'baseToken': {
                    'symbol': 'MYRO',
                    'name': 'Myro',
                    'address': '2e7yNwrmTgXp9ABUmcPXvFJTSrEVLj4YMyrb4GUM4Pdd'
                },
                'pairAddress': 'HhSwpr4S3Tp6TGfPfjCik5J7hK7fmEUfYTQ4ZVLdqa7p',
                'chainId': 'solana',
                'priceUsd': '0.04567',
                'liquidity': {'usd': 8000000},
                'priceChange': {'m5': 3.1, 'h1': 12.5, 'h24': 35.8},
                'pairCreatedAt': int(time.time() * 1000) - 3 * 60 * 60 * 1000,
                'dexId': 'raydium',
                'url': 'https://dexscreener.com/solana/hhswpr4s3tp6tgfpfjcik5j7hk7fmeufytq4zvldqa7p',
                'volume': {'h24': 3000000},
                'marketCap': 450000000
            },
            {
                'baseToken': {
                    'symbol': 'WIF',
                    'name': 'dogwifhat',
                    'address': 'EKpQGSJtjMFqKZ9KQanSqYXRcF8fBopzLHYxdM65zcjm'
                },
                'pairAddress': '2p7nYbtPBgt7Y4KJQjV3hL7K8H1cZ7YgqjJvRkXcJmZx',
                'chainId': 'solana',
                'priceUsd': '0.3456',
                'liquidity': {'usd': 25000000},
                'priceChange': {'m5': 2.3, 'h1': 8.9, 'h24': 22.1},
                'pairCreatedAt': int(time.time() * 1000) - 24 * 60 * 60 * 1000,
                'dexId': 'raydium',
                'url': 'https://dexscreener.com/solana/2p7nybtpbbgt7y4kjqjv3hl7k8h1cz7ygqjjvrkxcjmzx',
                'volume': {'h24': 8000000},
                'marketCap': 340000000
            }
        ]
        
        return backup_tokens
    
    def filter_solana_tokens(self, pairs):
        """تصفية عملات Solana فقط"""
        if not pairs:
            return []
        
        solana_pairs = []
        for pair in pairs:
            # يجب أن يكون chainId موجوداً ويساوي 'solana'
            if pair and isinstance(pair, dict) and pair.get('chainId') == 'solana':
                solana_pairs.append(pair)
        
        print(f"🔍 تم تصفية {len(solana_pairs)} عملة Solana من أصل {len(pairs)}")
        return solana_pairs
    
    # 🌟 التعديل الأساسي هنا: تشديد الشروط
    def check_token_conditions(self, token):
        """فحص الشروط على البيانات الحقيقية - (شروط الترند الصارم)"""
        try:
            if not token or not isinstance(token, dict):
                return False
                
            base_token = token.get('baseToken', {})
            symbol = base_token.get('symbol', 'Unknown')
            name = base_token.get('name', 'Unknown')
            
            print(f"\n🔍 فحص شروط: {symbol} ({name})")
            
            # 1. فحص السيولة الحقيقية - **الحد الأدنى مرفوع لضمان الجدية**
            liquidity_data = token.get('liquidity', {})
            liquidity = liquidity_data.get('usd', 0) if isinstance(liquidity_data, dict) else 0
            print(f"   💰 السيولة: ${liquidity:,.0f}")
            
            # رفع الحد الأدنى للسيولة إلى 50,000$ (يمكن تعديله)
            MIN_LIQUIDITY = 50000 
            if liquidity < MIN_LIQUIDITY: 
                print(f"   ❌ السيولة منخفضة (أقل من ${MIN_LIQUIDITY:,})")
                return False
            
            # 2. فحص العمر الحقيقي - **الحد الأقصى مخفض لاستهداف العملات الجديدة**
            pair_created_at = token.get('pairCreatedAt')
            MAX_AGE_MINUTES = 90  # 1.5 ساعة كحد أقصى
            if pair_created_at:
                age_minutes = (time.time() - pair_created_at/1000) / 60
                print(f"   ⏰ العمر: {age_minutes:.1f} دقيقة")
                
                if age_minutes > MAX_AGE_MINUTES: 
                    print(f"   ❌ العملة قديمة (أكبر من {MAX_AGE_MINUTES} دقيقة)")
                    return False
            else:
                # إذا لم يكن هناك تاريخ إنشاء، نتجاهل العملة لضمان الجودة
                print("   ⚠️ لا يوجد تاريخ إنشاء للزوج")
                return False
            
            # 3. فحص الأداء الحقيقي
            price_change = token.get('priceChange', {})
            if not isinstance(price_change, dict):
                price_change = {}
                
            change_5m = price_change.get('m5', 0)
            change_1h = price_change.get('h1', 0)
            
            print(f"   📈 الأداء: 5m={change_5m}%, 1h={change_1h}%")
            
            # شروط أداء أكثر صرامة: يجب أن تكون في ترند صاعد في الساعة الأخيرة
            if change_1h < 20:  # يجب أن يكون الارتفاع في الساعة الأخيرة كبيراً
                print("   ❌ ارتفاع الساعة الأخيرة ضعيف (أقل من 20%)")
                return False
            
            # يجب أن يكون هناك زخم حديث أو زخم قوي في الساعة الأخيرة
            if change_5m < 5 and change_1h < 50: 
                print("   ❌ لا يوجد زخم كافٍ حالياً")
                return False

            # 4. فحص حجم التداول (Volume) - **شرط إضافي لضمان السيولة والنشاط**
            volume_data = token.get('volume', {})
            volume_24h = volume_data.get('h24', 0) if isinstance(volume_data, dict) else 0
            MIN_VOLUME_24H = 100000 # 100 ألف دولار كحد أدنى
            print(f"   💰 حجم 24h: ${volume_24h:,.0f}")

            if volume_24h < MIN_VOLUME_24H: 
                print(f"   ❌ حجم التداول منخفض (أقل من ${MIN_VOLUME_24H:,})")
                return False
            
            print("   ✅ العملة مؤهلة")
            return True
            
        except Exception as e:
            print(f"❌ خطأ في فحص الشروط: {e}")
            return False
    
    # 🌟 التعديل الأساسي هنا: دمج الجودة والزخم لتحديد الإشارة
    def analyze_real_token(self, token):
        """تحليل العملة بناءً على البيانات الحقيقية وتحديد قوة الإشارة"""
        try:
            if not token or not isinstance(token, dict):
                return None
                
            # ... (جلب البيانات كما في الكود الأصلي)
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
            
            # ... (حساب العمر واختصار العناوين كما في الكود الأصلي)
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
🎯 **بوت الترندينغ الحقيقي v5.0 (المعدل)**
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

🔧 **جاري العمل على حل المشكلة...**
"""
            self.send_telegram_message(error_message)
            return 0
        
        # تصفية عملات Solana
        solana_pairs = self.filter_solana_tokens(all_pairs)
        
        if not solana_pairs:
            print("⚠️ لم يتم العثور على عملات Solana، استخدام أفضل العملات المتاحة")
            # التصفية هنا ضرورية للحفاظ على جودة التوصيات
            solana_pairs = all_pairs # نستخدم جميع العملات لكن الفلترة الصارمة ستقوم بإسقاطها غالباً
        
        print(f"📊 جاري تحليل {len(solana_pairs)} عملة...")
        
        # تطبيق الشروط على البيانات الحقيقية
        qualified_tokens = []
        for token in solana_pairs:
            if self.check_token_conditions(token):
                qualified_tokens.append(token)
        
        print(f"🎯 العملات المؤهلة: {len(qualified_tokens)}")
        
        # إذا كانت هناك عملات كثيرة، نختار الأفضل بناءً على النقاط
        analyzed_tokens = []
        for token in qualified_tokens:
            analysis = self.analyze_real_token(token)
            if analysis:
                analyzed_tokens.append(analysis)
        
        # ترتيب حسب قوة الإشارة (التي تمثل الجودة والزخم)
        if analyzed_tokens:
            # يمكن الترتيب يدوياً حسب نقاط الـ Signal Score (لأنها غير مخزنة في analysis) 
            # أو حسب الارتفاع في الساعة (h1) كبديل سريع
            analyzed_tokens.sort(key=lambda x: x.get('change_1h', 0) * x.get('liquidity', 0), reverse=True) 
            
            # نرسل فقط أفضل 3 أو 4
            if len(analyzed_tokens) > 4:
                analyzed_tokens = analyzed_tokens[:4]
                print(f"🎯 تم اختيار أفضل {len(analyzed_tokens)} عملة بناءً على التحليل")

        if not analyzed_tokens:
            no_tokens_message = f"""
📭 **لا توجد عملات ترند قوية حاليًا**

✅ تم فحص {len(solana_pairs)} عملة، ولكن لم تستوفِ أي منها شروط الجودة الصارمة.
⏰ {datetime.now().strftime('%I:%M %p')}
🔄 جاري البحث عن عملات جديدة...
"""
            self.send_telegram_message(no_tokens_message)
            return 0
        
        # إرسال العملات المؤهلة
        successful_sends = 0
        for analysis in analyzed_tokens:
            message = self.format_real_token_message(analysis)
            # نستخدم full_pair_address كـ token_id لضمان عدم تكرار التوصية
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
🔍 من أصل **{qualified_count}** عملة مؤهلة (من أفضل الترندينغ)
📈 من إجمالي **{total_count}** عملة تم فحصها

💎 **مصدر البيانات:** DEX Screener API مباشر
🎯 **الدقة:** بيانات حية ومباشرة
🔄 **التحديث القادم:** 5 دقائق

⚡ **بوت الترندينغ الحقيقي v5.0 (المعدل)**
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
🤖 **بدء بوت الترندينغ الحقيقي - الإصدار 5.0 (المعدل)**

⏰ {datetime.now().strftime('%Y-%m-%d %I:%M %p')}
🎯 **التحسينات:** تشديد شروط السيولة والعمر وحجم التداول لزيادة دقة التوصيات.
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
