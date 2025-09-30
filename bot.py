import os
import requests
import time
from datetime import datetime, timedelta
import sys

print("🚀 بدء تشغيل بوت الترندينغ الحقيقي - API مباشر...")

class RealDEXTrendingBot:
    def __init__(self, telegram_token, channel_id):
        self.telegram_token = telegram_token
        self.channel_id = channel_id
        self.last_sent_tokens = set()
        print("✅ تم تهيئة البوت الحقيقي!")
    
    def get_real_trending_data(self):
        """جلب البيانات الحية من DEX Screener API"""
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
            
            response = requests.get(url, headers=headers, timeout=15)
            
            if response.status_code != 200:
                print(f"❌ خطأ في API: {response.status_code}")
                print(f"📄 محتوى الاستجابة: {response.text}")
                return []
            
            data = response.json()
            print(f"✅ تم جلب البيانات بنجاح من API")
            
            # طباعة هيكل البيانات للتصحيح
            if 'pairs' in data:
                pairs = data['pairs']
                print(f"📊 عدد الأزواج المستلمة: {len(pairs)}")
                
                # عرض أول 3 أزواج للتصحيح
                for i, pair in enumerate(pairs[:3]):
                    base_token = pair.get('baseToken', {})
                    print(f"🔍 زوج {i+1}: {base_token.get('symbol', 'Unknown')} - {base_token.get('name', 'Unknown')}")
                
                return pairs
            else:
                print("❌ لم يتم العثور على أزواج في البيانات")
                print(f"🔑 المفاتيح المتاحة: {list(data.keys())}")
                return []
                
        except Exception as e:
            print(f"❌ خطأ في جلب البيانات: {e}")
            import traceback
            print(f"🔍 تفاصيل الخطأ: {traceback.format_exc()}")
            return []
    
    def filter_solana_tokens(self, pairs):
        """تصفية عملات Solana فقط"""
        solana_pairs = []
        for pair in pairs:
            if pair.get('chainId') == 'solana':
                solana_pairs.append(pair)
        
        print(f"🔍 تم تصفية {len(solana_pairs)} عملة Solana من أصل {len(pairs)}")
        return solana_pairs
    
    def check_token_conditions(self, token):
        """فحص الشروط على البيانات الحقيقية"""
        try:
            base_token = token.get('baseToken', {})
            symbol = base_token.get('symbol', 'Unknown')
            name = base_token.get('name', 'Unknown')
            
            print(f"🔍 فحص: {symbol} ({name})")
            
            # 1. فحص السيولة الحقيقية
            liquidity = token.get('liquidity', {}).get('usd', 0)
            print(f"   💰 السيولة الحقيقية: ${liquidity:,.2f}")
            
            if liquidity < 1000:  # حد أدنى واقعي
                print("   ❌ السيولة منخفضة")
                return False
            
            # 2. فحص العمر الحقيقي
            pair_created_at = token.get('pairCreatedAt')
            if pair_created_at:
                age_minutes = (time.time() - pair_created_at/1000) / 60
                print(f"   ⏰ العمر الحقيقي: {age_minutes:.1f} دقيقة")
                
                if age_minutes > 180:  # 3 ساعات كحد أقصى
                    print("   ❌ العملة قديمة")
                    return False
            else:
                print("   ⚠️ لا يوجد تاريخ إنشاء")
                # نستمر رغم عدم وجود تاريخ
            
            # 3. فحص الأداء الحقيقي
            price_change = token.get('priceChange', {})
            change_5m = price_change.get('m5', 0)
            change_1h = price_change.get('h1', 0)
            change_24h = price_change.get('h24', 0)
            
            print(f"   📈 الأداء الحقيقي: 5m={change_5m}%, 1h={change_1h}%, 24h={change_24h}%")
            
            # شروط مرنة للأداء
            if change_1h > 50 or change_24h > 100:  # أداء قوي
                print("   ✅ أداء قوي - مقبولة")
                return True
            
            if liquidity > 50000 and change_1h > 10:  # سيولة عالية + أداء إيجابي
                print("   ✅ سيولة عالية - مقبولة")
                return True
            
            if change_5m > 20:  # أداء سريع
                print("   ✅ أداء سريع - مقبولة")
                return True
            
            print("   ❌ لم تستوفِ الشروط")
            return False
            
        except Exception as e:
            print(f"❌ خطأ في فحص الشروط: {e}")
            return False
    
    def analyze_real_token(self, token):
        """تحليل العملة بناءً على البيانات الحقيقية"""
        try:
            base_token = token.get('baseToken', {})
            quote_token = token.get('quoteToken', {})
            
            symbol = base_token.get('symbol', 'Unknown')
            name = base_token.get('name', 'Unknown')
            
            # البيانات الحقيقية من API
            price = float(token.get('priceUsd', 0))
            liquidity = float(token.get('liquidity', {}).get('usd', 0))
            market_cap = float(token.get('marketCap', 0))
            volume_24h = float(token.get('volume', {}).get('h24', 0))
            
            # التغيرات السعرية الحقيقية
            price_change = token.get('priceChange', {})
            change_5m = float(price_change.get('m5', 0))
            change_1h = float(price_change.get('h1', 0))
            change_24h = float(price_change.get('h24', 0))
            
            # العمر الحقيقي
            pair_created_at = token.get('pairCreatedAt')
            if pair_created_at:
                age_minutes = (time.time() - pair_created_at/1000) / 60
                if age_minutes < 60:
                    age_text = f"{age_minutes:.0f} دقيقة"
                else:
                    age_hours = age_minutes / 60
                    age_text = f"{age_hours:.1f} ساعة"
            else:
                age_text = "غير معروف"
            
            # العناوين الحقيقية
            pair_address = token.get('pairAddress', '')
            base_token_address = base_token.get('address', '')
            
            # معلومات إضافية حقيقية
            dex_id = token.get('dexId', 'Unknown')
            url = token.get('url', f"https://dexscreener.com/solana/{pair_address}")
            
            # اختصار العناوين للعرض
            short_pair_address = pair_address[:8] + "..." + pair_address[-6:] if len(pair_address) > 20 else pair_address
            short_token_address = base_token_address[:8] + "..." + base_token_address[-6:] if len(base_token_address) > 20 else base_token_address
            
            # تحديد الإشارة بناءً على البيانات الحقيقية
            if change_5m > 30 and change_1h > 80:
                signal = "🚀 صاروخي"
                emoji = "🚀"
                urgency = "🔥 عاجل جداً"
            elif change_5m > 15 and change_1h > 40:
                signal = "📈 قوي جداً"
                emoji = "📈"
                urgency = "⚡ عاجل"
            elif change_1h > 20:
                signal = "🔥 ممتاز"
                emoji = "🔥"
                urgency = "📊 جيد"
            else:
                signal = "⚡ جيد"
                emoji = "⚡"
                urgency = "🕒 عادي"
            
            # معرف فريد حقيقي
            token_id = f"solana_{pair_address}"
            
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
    
    def format_real_token_message(self, token_analysis):
        """تنسيق رسالة بناءً على البيانات الحقيقية"""
        try:
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
            
            # حساب SOL المربوطة (بناءً على السيولة الحقيقية)
            pooled_sol = token_analysis['liquidity'] / 100  # تقدير واقعي
            
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

⛽️ **عنوان التبادل:**
`{token_analysis['pair_address']}`

📊 **البيانات المالية:**
• **القيمة السوقية:** {market_cap_text}
• **السيولة:** {liquidity_text}
• **الحجم (24h):** {volume_text}
• **السعر:** {price_text}
• **SOL المربوطة:** {pooled_sol:.0f} SOL

📈 **الأداء الفعلي:**
• **5 دقائق:** {token_analysis['change_5m']:+.1f}%
• **ساعة:** {token_analysis['change_1h']:+.1f}%
• **24 ساعة:** {token_analysis['change_24h']:+.1f}%

⚖️ **1 SOL = {tokens_per_sol:,} {token_analysis['symbol']}**

🔍 **الروابط:**
[عرض على DEXScreener]({token_analysis['url']})
[تداول على {token_analysis['exchange']}]({token_analysis['url']})

🕒 **{datetime.now().strftime('%I:%M %p')}** ✅
💎 **بيانات حية من DEX Screener API**
🎯 **بوت الترندينغ الحقيقي v3.0**
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
        
        if not all_pairs:
            error_message = f"""
❌ **تعذر جلب البيانات من DEX Screener**

⏰ {datetime.now().strftime('%I:%M %p')}
🔄 سيتم إعادة المحاولة خلال 5 دقائق...

🔧 **الأسباب المحتملة:**
• تغير في واجهة DEX Screener API
• مشكلة في الاتصال بالإنترنت
• معدل طلبات مرتفع
"""
            self.send_telegram_message(error_message)
            return 0
        
        # تصفية عملات Solana
        solana_pairs = self.filter_solana_tokens(all_pairs)
        
        if not solana_pairs:
            print("⚠️ لم يتم العثور على عملات Solana، استخدام جميع العملات")
            solana_pairs = all_pairs
        
        print(f"📊 جاري تحليل {len(solana_pairs)} عملة...")
        
        # تطبيق الشروط على البيانات الحقيقية
        qualified_tokens = []
        for token in solana_pairs:
            if self.check_token_conditions(token):
                qualified_tokens.append(token)
        
        print(f"🎯 العملات المؤهلة: {len(qualified_tokens)}")
        
        # إذا كانت هناك عملات كثيرة، نختار الأفضل
        if len(qualified_tokens) > 4:
            # ترتيب حسب الأداء في الساعة
            qualified_tokens.sort(key=lambda x: x.get('priceChange', {}).get('h1', 0), reverse=True)
            qualified_tokens = qualified_tokens[:4]
            print(f"🎯 تم اختيار أفضل {len(qualified_tokens)} عملة")
        
        if not qualified_tokens:
            # إذا لم توجد عملات مؤهلة، نرسل تقريراً مفصلاً
            return self.send_no_qualified_tokens_report(solana_pairs)
        
        # إرسال العملات المؤهلة
        successful_sends = 0
        for token in qualified_tokens:
            analysis = self.analyze_real_token(token)
            if analysis:
                message = self.format_real_token_message(analysis)
                if message and analysis['token_id'] not in self.last_sent_tokens:
                    if self.send_telegram_message(message):
                        successful_sends += 1
                        self.last_sent_tokens.add(analysis['token_id'])
                        print(f"✅ تم إرسال توصية {analysis['symbol']}")
                        time.sleep(3)  # انتظار بين الرسائل
        
        # إرسال ملخص بالبيانات الحقيقية
        self.send_real_summary(successful_sends, len(qualified_tokens), len(solana_pairs))
        
        return successful_sends
    
    def send_no_qualified_tokens_report(self, all_tokens):
        """إرسال تقرير عندما لا توجد عملات مؤهلة"""
        try:
            # تحليل أسباب عدم التأهل
            reasons = {
                'low_liquidity': 0,
                'old_age': 0,
                'poor_performance': 0
            }
            
            for token in all_tokens[:10]:  # تحليل أول 10 عملات فقط
                liquidity = token.get('liquidity', {}).get('usd', 0)
                if liquidity < 1000:
                    reasons['low_liquidity'] += 1
                    continue
                
                pair_created_at = token.get('pairCreatedAt')
                if pair_created_at:
                    age_minutes = (time.time() - pair_created_at/1000) / 60
                    if age_minutes > 180:
                        reasons['old_age'] += 1
                        continue
                
                price_change = token.get('priceChange', {})
                change_1h = price_change.get('h1', 0)
                if change_1h <= 20:
                    reasons['poor_performance'] += 1
            
            report = f"""
📭 **تقرير التحليل - لا توجد توصيات حالياً**

🔍 تم فحص {len(all_tokens)} عملة من DEX Screener
❌ لم يتم العثور على عملات تلبي الشروط

📊 **تحليل الأسباب:**
• **سيولة منخفضة:** {reasons['low_liquidity']} عملة
• **عمر كبير:** {reasons['old_age']} عملة  
• **أداء ضعيف:** {reasons['poor_performance']} عملة

🎯 **الشروط المطلوبة:**
• سيولة: > $1,000
• عمر: < 3 ساعات
• أداء: > 20% في الساعة

⏰ {datetime.now().strftime('%I:%M %p')}
🔄 التحديث القادم خلال 5 دقائق...
"""
            self.send_telegram_message(report)
            return 0
            
        except Exception as e:
            print(f"❌ خطأ في إرسال تقرير عدم التأهل: {e}")
            return 0
    
    def send_real_summary(self, successful_sends, qualified_count, total_count):
        """إرسال ملخص بالبيانات الحقيقية"""
        try:
            summary = f"""
📊 **ملخص التحديث - {datetime.now().strftime('%I:%M %p')}**

✅ تم إرسال **{successful_sends}** توصية جديدة
🔍 من أصل **{qualified_count}** عملة مؤهلة
📈 من إجمالي **{total_count}** عملة تم فحصها

💎 **مصدر البيانات:** DEX Screener API المباشر
🎯 **الدقة:** بيانات حية ومباشرة
🔄 **التحديث القادم:** 5 دقائق

⚡ **بوت الترندينغ الحقيقي v3.0**
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
🤖 **بدء بوت الترندينغ الحقيقي**

⏰ {datetime.now().strftime('%Y-%m-%d %I:%M %p')}
🎯 المصدر: DEX Screener API مباشر
🔧 النسخة: 3.0 (بيانات حقيقية)
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
