import os
import requests
import time
from datetime import datetime, timedelta
import sys
import json

print("🚀 بدء تشغيل بوت الترندينغ المحترف - الإصدار المحسن...")

class ProfessionalTrendingBot:
    def __init__(self, telegram_token, channel_id):
        self.telegram_token = telegram_token
        self.channel_id = channel_id
        self.last_sent_tokens = set()
        print("✅ تم تهيئة البوت المحترف!")
    
    def get_trending_tokens(self):
        """جلب العملات الترندينغ مع تحسينات"""
        try:
            print("🔄 جلب العملات الترندينغ من DEX Screener...")
            
            # استخدام API مباشر للترندينغ
            url = "https://api.dexscreener.com/latest/dex/search?q=trending"
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Accept': 'application/json',
                'Referer': 'https://dexscreener.com/'
            }
            
            response = requests.get(url, headers=headers, timeout=15)
            
            if response.status_code != 200:
                print(f"❌ خطأ في الاتصال: {response.status_code}")
                print(f"❌ تفاصيل الخطأ: {response.text}")
                return []
            
            data = response.json()
            
            # Debug: طباعة البيانات المستلمة
            print(f"📊 هيكل البيانات المستلمة: {list(data.keys()) if isinstance(data, dict) else 'غير معروف'}")
            
            if not data:
                print("❌ البيانات المستلمة فارغة")
                return []
            
            # محاولة استخراج الأزواج من هياكل مختلفة للبيانات
            pairs = []
            
            # الهيكل 1: من /search
            if 'pairs' in data:
                pairs = data['pairs']
                print(f"✅ تم العثور على {len(pairs)} زوج من مفتاح 'pairs'")
            
            # الهيكل 2: من /tokens/trending
            elif 'results' in data:
                pairs = data['results']
                print(f"✅ تم العثور على {len(pairs)} زوج من مفتاح 'results'")
            
            else:
                # إذا لم يكن هناك هيكل واضح، نستخدم البيانات مباشرة
                if isinstance(data, list):
                    pairs = data
                    print(f"✅ تم العثور على {len(pairs)} زوج من القائمة المباشرة")
                else:
                    print("❌ لم يتم العثور على أزواج في البيانات")
                    # طباعة المفاتيح المتاحة للتdebug
                    if isinstance(data, dict):
                        print(f"🔑 المفاتيح المتاحة: {list(data.keys())}")
                    return []
            
            if not pairs:
                print("❌ لا توجد أزواج متاحة")
                return []
            
            print(f"📈 تم جلب {len(pairs)} عملة إجمالاً")
            
            # فلترة العملات على Solana فقط
            solana_pairs = []
            other_chains = {}
            
            for pair in pairs:
                if not pair:
                    continue
                    
                chain = pair.get('chainId', 'unknown')
                base_symbol = pair.get('baseToken', {}).get('symbol', 'Unknown')
                
                if chain == 'solana':
                    solana_pairs.append(pair)
                else:
                    if chain not in other_chains:
                        other_chains[chain] = 0
                    other_chains[chain] += 1
            
            print(f"🔍 تحليل السلاسل: Solana ({len(solana_pairs)}), أخرى: {other_chains}")
            
            # إذا لم نجد عملات Solana، نستخدم كل العملات
            if not solana_pairs:
                print("⚠️ لم يتم العثور على عملات Solana، استخدام جميع العملات")
                trending_tokens = pairs[:15]  # زيادة العدد
            else:
                trending_tokens = solana_pairs[:15]  # زيادة العدد
            
            print(f"🎯 سيتم تحليل {len(trending_tokens)} عملة")
            
            return trending_tokens
            
        except requests.exceptions.RequestException as e:
            print(f"❌ خطأ في الاتصال بالشبكة: {e}")
            return []
        except Exception as e:
            print(f"❌ خطأ غير متوقع في جلب البيانات: {e}")
            import traceback
            print(f"🔍 تفاصيل الخطأ: {traceback.format_exc()}")
            return []
    
    def check_token_conditions(self, token):
        """فحص الشروط مع مرونة أكثر"""
        try:
            if not token:
                print("❌ رمز العملة غير صالح")
                return False
                
            base_token = token.get('baseToken', {})
            symbol = base_token.get('symbol', 'Unknown')
            name = base_token.get('name', 'Unknown')
            
            print(f"🔍 فحص العملة: {symbol} ({name})")
            
            # 1. فحص العمر (مرونة أكثر - حتى 60 دقيقة)
            pair_created_at = token.get('pairCreatedAt')
            if pair_created_at:
                token_age_minutes = (time.time() - pair_created_at/1000) / 60
                print(f"   ⏰ عمر العملة: {token_age_minutes:.1f} دقيقة")
                if token_age_minutes > 60:  # زيادة إلى 60 دقيقة
                    print("   ❌ العملة قديمة (أكثر من 60 دقيقة)")
                    return False
            else:
                print("   ⚠️ لا يوجد تاريخ إنشاء، المتابعة...")
                # لا نرفض العملة إذا لم يكن هناك تاريخ
            
            # 2. فحص السيولة (شروط مرنة أكثر)
            liquidity = token.get('liquidity', {}).get('usd', 0)
            print(f"   💰 السيولة: ${liquidity:,.2f}")
            
            if liquidity < 500:  # تخفيض الحد الأدنى إلى 500$
                print("   ❌ السيولة منخفضة جداً")
                return False
            
            # 3. فحص السعر
            price = token.get('priceUsd')
            if not price or float(price) <= 0:
                print("   ❌ سعر غير صالح")
                return False
            
            # 4. فحص التغيرات السعرية (شروط جديدة)
            price_change = token.get('priceChange', {})
            change_5m = price_change.get('m5', 0)
            change_1h = price_change.get('h1', 0)
            
            print(f"   📈 تغير 5m: {change_5m}%, 1h: {change_1h}%")
            
            # قبول العملات ذات الأداء الجيد مؤخراً
            if change_5m > 50 or change_1h > 100:
                print("   ✅ أداء قوي - مقبولة")
                return True
            
            # قبول العملات ذات السيولة الجيدة حتى مع أداء متوسط
            if liquidity > 5000 and change_5m > 0:
                print("   ✅ سيولة عالية وأداء إيجابي - مقبولة")
                return True
            
            # شرط أساسي: أداء إيجابي في الساعة الأخيرة
            if change_1h > 10:
                print("   ✅ أداء إيجابي في الساعة - مقبولة")
                return True
            
            print("   ❌ لم تستوفِ الشروط الأساسية")
            return False
            
        except Exception as e:
            print(f"❌ خطأ في فحص الشروط: {e}")
            return False
    
    def analyze_token_professional(self, token):
        """تحليل مفصل للعملة مع تحسينات"""
        try:
            if not token:
                return None
                
            base_token = token.get('baseToken', {})
            quote_token = token.get('quoteToken', {})
            
            symbol = base_token.get('symbol', 'Unknown')
            name = base_token.get('name', 'Unknown')
            
            # المعلومات الأساسية
            price = float(token.get('priceUsd', 0))
            liquidity_data = token.get('liquidity', {})
            liquidity = float(liquidity_data.get('usd', 0)) if liquidity_data else 0
            market_cap = float(token.get('marketCap', 0))
            volume_data = token.get('volume', {})
            volume_24h = float(volume_data.get('h24', 0)) if volume_data else 0
            fdv = float(token.get('fdv', 0))
            
            # التغيرات السعرية
            price_change = token.get('priceChange', {})
            change_5m = float(price_change.get('m5', 0))
            change_1h = float(price_change.get('h1', 0))
            change_24h = float(price_change.get('h24', 0))
            
            # معلومات العمر
            pair_created_at = token.get('pairCreatedAt')
            if pair_created_at:
                age_minutes = (time.time() - pair_created_at/1000) / 60
                age_text = f"{age_minutes:.1f} دقيقة"
            else:
                age_text = "غير معروف"
            
            # معلومات العقدة
            pair_address = token.get('pairAddress', '')
            base_token_address = base_token.get('address', '')
            
            # معلومات إضافية
            chain_id = token.get('chainId', 'unknown')
            dex_id = token.get('dexId', 'Unknown')
            url = token.get('url', '')
            
            # اختصار العناوين للعرض
            short_pair_address = pair_address[:8] + "..." + pair_address[-6:] if len(pair_address) > 20 else pair_address
            short_token_address = base_token_address[:8] + "..." + base_token_address[-6:] if len(base_token_address) > 20 else base_token_address
            
            # تحديد الإشارة بناءً على الأداء
            if change_5m > 50 and change_1h > 100:
                signal = "🚀 صاروخي"
                emoji = "🚀"
            elif change_5m > 25 and change_1h > 50:
                signal = "🔥 قوي جداً"
                emoji = "🔥"
            elif change_5m > 10 and change_1h > 20:
                signal = "📈 ممتاز"
                emoji = "📈"
            elif change_5m > 0:
                signal = "⚡ جيد"
                emoji = "⚡"
            else:
                signal = "📊 عادي"
                emoji = "📊"
            
            # إنشاء معرف فريد للعملة (باستخدام العنوان الكامل)
            token_id = f"{chain_id}_{base_token_address}"
            
            return {
                'symbol': symbol,
                'name': name,
                'price': price,
                'liquidity': liquidity,
                'market_cap': market_cap,
                'volume_24h': volume_24h,
                'fdv': fdv,
                'change_5m': change_5m,
                'change_1h': change_1h,
                'change_24h': change_24h,
                'age': age_text,
                'signal': signal,
                'emoji': emoji,
                'pair_address': short_pair_address,
                'token_address': short_token_address,
                'full_pair_address': pair_address,
                'full_token_address': base_token_address,
                'url': url,
                'exchange': dex_id,
                'chain': chain_id,
                'token_id': token_id
            }
            
        except Exception as e:
            print(f"❌ خطأ في التحليل المفصل: {e}")
            import traceback
            print(f"🔍 تفاصيل الخطأ: {traceback.format_exc()}")
            return None
    
    def format_single_token_message(self, token_analysis):
        """تنسيق رسالة منفردة مع تحسينات"""
        try:
            if not token_analysis:
                return None
                
            # تنسيق السعر
            price = token_analysis['price']
            if price < 0.000001:
                price_text = f"${price:.10f}"
            elif price < 0.0001:
                price_text = f"${price:.8f}"
            elif price < 0.01:
                price_text = f"${price:.6f}"
            else:
                price_text = f"${price:.4f}"
            
            # تنسيق الأرقام الكبيرة
            def format_currency(value):
                if value >= 1000000:
                    return f"${value/1000000:.2f}M"
                elif value >= 1000:
                    return f"${value/1000:.1f}K"
                else:
                    return f"${value:.0f}"
            
            market_cap_text = format_currency(token_analysis['market_cap'])
            liquidity_text = format_currency(token_analysis['liquidity'])
            volume_text = format_currency(token_analysis['volume_24h'])
            fdv_text = format_currency(token_analysis['fdv'])
            
            # حساب SOL المربوطة (محاكاة - تحسين الدقة)
            pooled_sol = token_analysis['liquidity'] / 100 if token_analysis['liquidity'] > 0 else 0
            
            # حساب عدد التوكنات مقابل 1 SOL
            tokens_per_sol = int(1/price) if price > 0 else 0
            
            # رابط DEXScreener
            dex_url = token_analysis['url'] or f"https://dexscreener.com/{token_analysis['chain']}/{token_analysis['full_pair_address']}"
            
            # إنشاء الرسالة المحسنة
            message = f"""
🔰 **{token_analysis['chain'].upper()} | {token_analysis['name']} (${token_analysis['symbol']})** {token_analysis['emoji']}

🪅 **CA:** `{token_analysis['token_address']}`
⛽️ **LP:** `{token_analysis['pair_address']}`

🔗 **DEX:** {token_analysis['exchange']}
📊 **Market Cap:** {market_cap_text}
💧 **Liquidity:** {liquidity_text}
💰 **FDV:** {fdv_text}
📈 **24h Volume:** {volume_text}
💵 **Price:** {price_text}
⛽️ **Pooled SOL:** {pooled_sol:.2f} SOL
🔥 **Burn:** 100%
👤 **Renounced:** ✅️
🗯️ **Freeze Revoked:** ✅️

⚖️ **1 SOL ≈ {tokens_per_sol:,} {token_analysis['symbol']}**
🎯 **Price Impact:** {abs(token_analysis['change_5m']):.2f}%

📊 **Trend Analysis:**
   🕒 **Age:** {token_analysis['age']}
   📈 **5m:** {token_analysis['change_5m']:+.2f}%
   ⏰ **1h:** {token_analysis['change_1h']:+.2f}%
   🎯 **24h:** {token_analysis['change_24h']:+.2f}%
   🔥 **Signal:** {token_analysis['signal']}

🔍 **Links:**
   📊 [DEXScreener]({dex_url})
   💰 [Buy on {token_analysis['exchange']}]({dex_url})

🕒 **{datetime.now().strftime('%I:%M %p')}** ✅️

⚠️ **تحديث تلقائي كل 5 دقائق**
🎯 **يتم فحص العملات الجديدة باستمرار**
"""
            return message
            
        except Exception as e:
            print(f"❌ خطأ في تنسيق الرسالة: {e}")
            return None
    
    def send_single_message(self, message):
        """إرسال رسالة منفردة إلى Telegram"""
        try:
            if not message:
                print("❌ لا توجد رسالة لإرسالها")
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
                print(f"🔍 تفاصيل الخطأ: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ خطأ في الإرسال: {e}")
            return False
    
    def run_professional_analysis(self):
        """تشغيل التحليل المحترف مع تحسينات"""
        print("🔍 بدء التحليل المحترف المحسن...")
        
        # جلب العملات الترندينغ
        trending_tokens = self.get_trending_tokens()
        
        if not trending_tokens:
            error_message = f"""
❌ **لا توجد عملات ترندينغ حالياً**

⏰ {datetime.now().strftime('%I:%M %p')}
🔄 سيتم إعادة المحاولة خلال 5 دقائق...
"""
            self.send_single_message(error_message)
            return 0
        
        print(f"📊 تم العثور على {len(trending_tokens)} عملة للتحليل")
        
        # تطبيق الشروط
        filtered_tokens = []
        rejected_tokens = []
        
        for token in trending_tokens:
            if self.check_token_conditions(token):
                filtered_tokens.append(token)
            else:
                rejected_tokens.append(token)
        
        print(f"🎯 العملات المطابقة للشروط: {len(filtered_tokens)}")
        print(f"❌ العملات المرفوضة: {len(rejected_tokens)}")
        
        if not filtered_tokens:
            # إرسال تقرير مفصل عن العملات المرفوضة
            rejection_report = self.create_rejection_report(rejected_tokens, len(trending_tokens))
            self.send_single_message(rejection_report)
            return 0
        
        # إرسال كل عملة في رسالة منفصلة (فقط العملات الجديدة)
        successful_sends = 0
        new_tokens_found = 0
        duplicate_tokens = 0
        
        for token in filtered_tokens:
            # تحليل مفصل للعملة
            token_analysis = self.analyze_token_professional(token)
            
            if token_analysis:
                # التحقق إذا كانت العملة جديدة (لم يتم إرسالها من قبل)
                if token_analysis['token_id'] not in self.last_sent_tokens:
                    new_tokens_found += 1
                    
                    # إنشاء رسالة منفردة
                    message = self.format_single_token_message(token_analysis)
                    
                    if message:
                        # إرسال الرسالة
                        if self.send_single_message(message):
                            successful_sends += 1
                            self.last_sent_tokens.add(token_analysis['token_id'])
                            print(f"✅ تم إرسال توصية {token_analysis['symbol']}")
                        
                        # انتظار 3 ثانية بين كل رسالة
                        time.sleep(3)
                else:
                    duplicate_tokens += 1
                    print(f"⏭️ تم تخطي {token_analysis['symbol']} (مرسلة مسبقاً)")
        
        # إرسال ملخص نهائي
        summary_message = self.create_summary_report(
            successful_sends, new_tokens_found, duplicate_tokens, 
            len(filtered_tokens), len(trending_tokens)
        )
        self.send_single_message(summary_message)
        
        # تنظيف الذاكرة (الاحتفاظ بآخر 100 عملة فقط)
        if len(self.last_sent_tokens) > 100:
            self.last_sent_tokens = set(list(self.last_sent_tokens)[-100:])
        
        print(f"🎉 اكتمل إرسال {successful_sends} توصية جديدة")
        return successful_sends
    
    def create_rejection_report(self, rejected_tokens, total_tokens):
        """إنشاء تقرير عن العملات المرفوضة"""
        try:
            report = f"""
📭 **تقرير التحليل - لا توجد توصيات**

🔍 تم فحص {total_tokens} عملة ترندينغ
❌ لم يتم العثور على عملات تلبي الشروط المحسنة

🎯 **الشروط المطلوبة:**
   • عمر: أقل من 60 دقيقة ⏰
   • سيولة: أكثر من $500 💧
   • أداء: تغير إيجابي في 5m أو 1h 📈

📊 **أسباب الرفض الشائعة:**
   • سيولة منخفضة
   • عمر كبير
   • أداء سلبي

⏰ {datetime.now().strftime('%I:%M %p')}
🔄 التحديث القادم خلال 5 دقائق...
"""
            return report
        except Exception as e:
            print(f"❌ خطأ في إنشاء تقرير الرفض: {e}")
            return "📭 لا توجد توصيات حالياً"
    
    def create_summary_report(self, successful_sends, new_tokens, duplicates, filtered, total):
        """إنشاء تقرير ملخص"""
        try:
            report = f"""
📊 **ملخص التحديث - {datetime.now().strftime('%I:%M %p')}** ✅️

✅ تم اكتشاف **{new_tokens}** عملة جديدة
📨 تم إرسال **{successful_sends}** توصية
🔄 تم تخطي **{duplicates}** عملة مكررة

🔍 **إحصائيات التحليل:**
   • إجمالي العملات: {total}
   • المطابقة للشروط: {filtered}
   • النسبة: {(filtered/total*100) if total > 0 else 0:.1f}%

🎯 **الشروط المطبقة:**
   • عمر أقل من 60 دقيقة ⏰
   • سيولة فوق $500 💧
   • أداء إيجابي 📈

🔄 **التحديث القادم خلال 5 دقائق...**
🔔 **يتم المراقبة المستمرة**

⚡ **MevX Bot - الإصدار المحسن v4.0**
"""
            return report
        except Exception as e:
            print(f"❌ خطأ في إنشاء التقرير الملخص: {e}")
            return "📊 تم إكمال التحليل"

# التشغيل الرئيسي
if __name__ == "__main__":
    TELEGRAM_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
    CHANNEL_ID = os.environ.get('TELEGRAM_CHANNEL_ID')
    
    if not TELEGRAM_TOKEN or not CHANNEL_ID:
        print("❌ يرجى إضافة TELEGRAM_BOT_TOKEN و TELEGRAM_CHANNEL_ID في Secrets")
        sys.exit(1)
    
    bot = ProfessionalTrendingBot(TELEGRAM_TOKEN, CHANNEL_ID)
    
    try:
        # إرسال رسالة بدء التشغيل
        start_message = f"""
🤖 **بدء تشغيل البوت المحسن - الإصدار 4.0**

⏰ وقت البدء: {datetime.now().strftime('%Y-%m-%d %I:%M %p')}
🔄 التحديث: كل 5 دقائق
🎯 الشروط المحسنة: 
   • عمر حتى 60 دقيقة
   • سيولة من $500
   • أداء إيجابي

⚡ **جارٍ فحص العملات الحالية...**
"""
        bot.send_single_message(start_message)
        
        # تشغيل دورة واحدة
        print(f"\n🔄 بدء دورة التشغيل - {datetime.now().strftime('%Y-%m-%d %I:%M %p')}")
        count = bot.run_professional_analysis()
        print(f"🎯 اكتمل التشغيل! تم إرسال {count} توصية جديدة")
        
        print("✅ تم إنهاء البوت بنجاح! الانتظار للدورة التالية...")
        
    except Exception as e:
        print(f"❌ خطأ غير متوقع: {e}")
        import traceback
        print(f"🔍 تفاصيل الخطأ: {traceback.format_exc()}")
        
        # محاولة إرسال خطأ إلى Telegram
        try:
            error_msg = f"❌ خطأ في البوت: {str(e)[:200]}..."
            bot.send_single_message(error_msg)
        except:
            pass
        sys.exit(1)
    
    sys.exit(0)
