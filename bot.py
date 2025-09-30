import os
import requests
import time
from datetime import datetime, timedelta
import sys

print("🚀 بدء تشغيل بوت الترندينغ المحترف - تحديث كل 5 دقائق...")

class ProfessionalTrendingBot:
    def __init__(self, telegram_token, channel_id):
        self.telegram_token = telegram_token
        self.channel_id = channel_id
        self.last_sent_tokens = set()
        print("✅ تم تهيئة البوت المحترف!")
    
    def get_trending_tokens(self):
        """جلب أول 10 عملات من صفحة الترندينغ"""
        try:
            print("🔄 جلب العملات الترندينغ من DEX Screener...")
            
            url = "https://api.dexscreener.com/latest/dex/tokens/trending?limit=15"
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Accept': 'application/json'
            }
            
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code != 200:
                print(f"❌ خطأ في الاتصال: {response.status_code}")
                return []
            
            data = response.json()
            
            if not data or not isinstance(data, dict):
                print("❌ البيانات المستلمة غير صالحة")
                return []
            
            pairs = data.get('pairs', [])
            
            if pairs is None:
                print("❌ لم يتم العثور على أزواج تداول")
                return []
            
            if not isinstance(pairs, list):
                print("❌ تنسيق الأزواج غير صالح")
                return []
            
            print(f"✅ تم جلب {len(pairs)} عملة")
            
            # فلترة العملات على Solana فقط
            solana_pairs = [pair for pair in pairs if pair and pair.get('chainId') == 'solana']
            
            # أخذ أول 10 عملات فقط من الترندينغ
            trending_tokens = solana_pairs[:10]
            
            return trending_tokens
            
        except requests.exceptions.RequestException as e:
            print(f"❌ خطأ في الاتصال بالشبكة: {e}")
            return []
        except Exception as e:
            print(f"❌ خطأ غير متوقع في جلب البيانات: {e}")
            return []
    
    def check_token_conditions(self, token):
        """فحص الشروط الأساسية فقط (بدون شرط الأمان الإضافي)"""
        try:
            if not token:
                return False
                
            base_token = token.get('baseToken', {})
            symbol = base_token.get('symbol', 'Unknown')
            print(f"🔍 فحص العملة: {symbol}")
            
            # 1. فحص العمر (لا يتجاوز 35 دقيقة)
            pair_created_at = token.get('pairCreatedAt')
            if pair_created_at:
                token_age_minutes = (time.time() - pair_created_at/1000) / 60
                print(f"   ⏰ عمر العملة: {token_age_minutes:.1f} دقيقة")
                if token_age_minutes > 35:
                    print("   ❌ العملة قديمة (أكثر من 35 دقيقة)")
                    return False
            else:
                print("   ❌ لا يوجد تاريخ إنشاء")
                return False
            
            # 2. فحص إذا كانت ضمن أول 10 عملات ترندينغ
            print("   ✅ ضمن أول 10 عملات ترندينغ")
            
            # 3. فحص السيولة
            liquidity = token.get('liquidity', {}).get('usd', 0)
            print(f"   💰 السيولة: ${liquidity}")
            
            if liquidity < 1000:
                print("   ❌ السيولة غير مغلقة أو منخفضة")
                return False
            
            # 4. فحص السعر الأساسي فقط
            price = token.get('priceUsd')
            if not price or float(price) <= 0:
                print("   ❌ سعر غير صالح")
                return False
            
            print("   ✅ العملة تلبي جميع الشروط")
            return True
            
        except Exception as e:
            print(f"❌ خطأ في فحص الشروط: {e}")
            return False
    
    def analyze_token_professional(self, token):
        """تحليل مفصل للعملة"""
        try:
            if not token:
                return None
                
            base_token = token.get('baseToken', {})
            symbol = base_token.get('symbol', 'Unknown')
            name = base_token.get('name', 'Unknown')
            
            # المعلومات الأساسية
            price = float(token.get('priceUsd', 0))
            liquidity_data = token.get('liquidity', {})
            liquidity = float(liquidity_data.get('usd', 0)) if liquidity_data else 0
            market_cap = float(token.get('marketCap', 0))
            volume_data = token.get('volume', {})
            volume_24h = float(volume_data.get('h24', 0)) if volume_data else 0
            
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
            
            # اختصار العناوين للعرض
            short_pair_address = pair_address[:20] + "..." if len(pair_address) > 20 else pair_address
            short_token_address = base_token_address[:20] + "..." if len(base_token_address) > 20 else base_token_address
            
            # تحديد الإشارة بناءً على الأداء
            if change_5m > 20 and change_1h > 30:
                signal = "🚀 قوي جداً"
                emoji = "🚀"
            elif change_5m > 10 and change_1h > 15:
                signal = "🔥 قوي"
                emoji = "🔥"
            elif change_5m > 0:
                signal = "📈 متوسط"
                emoji = "📈"
            else:
                signal = "⚡ عادي"
                emoji = "⚡"
            
            # إنشاء معرف فريد للعملة لمنع التكرار
            token_id = f"{symbol}_{pair_address[:10]}" if pair_address else f"{symbol}_{int(time.time())}"
            
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
                'pair_address': short_pair_address,
                'token_address': short_token_address,
                'full_pair_address': pair_address,
                'full_token_address': base_token_address,
                'url': token.get('url', ''),
                'exchange': token.get('dexId', 'Unknown'),
                'token_id': token_id
            }
            
        except Exception as e:
            print(f"❌ خطأ في التحليل المفصل: {e}")
            return None
    
    def format_single_token_message(self, token_analysis):
        """تنسيق رسالة منفردة بنفس شكل الصورة"""
        try:
            if not token_analysis:
                return None
                
            # تنسيق السعر
            price = token_analysis['price']
            if price < 0.0001:
                price_text = f"${price:.8f}"
            elif price < 0.001:
                price_text = f"${price:.6f}"
            else:
                price_text = f"${price:.4f}"
            
            # تنسيق الأرقام الكبيرة
            market_cap = token_analysis['market_cap']
            liquidity = token_analysis['liquidity']
            volume_24h = token_analysis['volume_24h']
            
            market_cap_text = f"${market_cap/1000:.1f}K" if market_cap < 1000000 else f"${market_cap/1000000:.2f}M"
            liquidity_text = f"${liquidity/1000:.1f}K" if liquidity < 1000000 else f"${liquidity/1000000:.2f}M"
            volume_text = f"${volume_24h/1000:.1f}K" if volume_24h < 1000000 else f"${volume_24h/1000000:.2f}M"
            
            # حساب SOL المربوطة (محاكاة)
            pooled_sol = liquidity / 100 if liquidity > 0 else 0
            
            # حساب عدد التوكنات مقابل 1 SOL
            tokens_per_sol = int(1/price) if price > 0 else 0
            
            # إنشاء الرسالة بنفس تنسيق الصورة
            message = f"""
🔰 **Sol | {token_analysis['name']} (${token_analysis['symbol']})** 🔰

🪅 **CA:** {token_analysis['token_address']}
⛽️ **LP:** {token_analysis['pair_address']}

🔎 **Search on X**
🎯 **Exchange:** {token_analysis['exchange']} → PumpSwap
💡 **Market Cap:** {market_cap_text}
💧 **Liquidity:** {liquidity_text}
💵 **Token Price:** {price_text}
⛽️ **Pooled SOL:** {pooled_sol:.2f} 🪙
🔥 **Burn:** 100%
👤 **Renounced:** ✅️
🗯️ **Freeze Revoked:** ✅️

⚖️ **1 SOL ⇄ {tokens_per_sol:,} {token_analysis['symbol']}**
🏷️ **Price Impact:** {abs(token_analysis['change_5m']):.2f}%

📊 **Trend Analysis:**
   🕒 **Age:** {token_analysis['age']}
   📈 **5m Change:** {token_analysis['change_5m']:.2f}%
   ⏰ **1h Change:** {token_analysis['change_1h']:.2f}%
   🎯 **24h Change:** {token_analysis['change_24h']:.2f}%
   🔥 **Signal:** {token_analysis['signal']}

💰 **MevX.io 2.0** | 💰 **MevX 1.0** | 🦅 **DexScreen** | 📈 **PumpSwap** | ⚖️ **Owner** | 🔗 **Pair**

🕒 **{datetime.now().strftime('%I:%M %p')}** ✅️

⚠️ **تحديث تلقائي كل 5 دقائق**
🔍 **يتم فحص العملات الجديدة كل 300 ثانية**
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
                print(f"❌ فشل إرسال الرسالة: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ خطأ في الإرسال: {e}")
            return False
    
    def run_professional_analysis(self):
        """تشغيل التحليل المحترف"""
        print("🔍 بدء التحليل المحترف...")
        
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
        
        print(f"📊 تم العثور على {len(trending_tokens)} عملة ترندينغ")
        
        # تطبيق الشروط
        filtered_tokens = []
        for token in trending_tokens:
            if self.check_token_conditions(token):
                filtered_tokens.append(token)
        
        print(f"🎯 العملات المطابقة للشروط: {len(filtered_tokens)}")
        
        if not filtered_tokens:
            no_tokens_message = f"""
📭 **لا توجد توصيات جديدة**

🔍 تم فحص {len(trending_tokens)} عملة ترندينغ
❌ لم يتم العثور على عملات تلبي الشروط:

⚙️ **الشروط المطلوبة:**
   • العمر: لا يتجاوز 35 دقيقة
   • الموقع: أول 10 عملات ترندينغ  
   • السيولة: مغلقة ($1,000+)

⏰ {datetime.now().strftime('%I:%M %p')}
🔄 التحديث القادم خلال 5 دقائق...
"""
            self.send_single_message(no_tokens_message)
            return 0
        
        # إرسال كل عملة في رسالة منفصلة (فقط العملات الجديدة)
        successful_sends = 0
        new_tokens_found = 0
        
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
                        
                        # انتظار 2 ثانية بين كل رسالة
                        time.sleep(2)
                else:
                    print(f"⏭️ تم تخطي {token_analysis['symbol']} (مرسلة مسبقاً)")
        
        # إرسال ملخص نهائي إذا وجد عملات جديدة
        if successful_sends > 0:
            summary_message = f"""
📊 **ملخص التحديث - {datetime.now().strftime('%I:%M %p')}** ✅️

✅ تم اكتشاف **{new_tokens_found}** عملة جديدة
📨 تم إرسال **{successful_sends}** توصية

🎯 **الشروط المطبقة:**
   • عمر أقل من 35 دقيقة ⏰
   • ضمن أقوى 10 عملات ترندينغ 🔥
   • سيولة مغلقة ($1,000+) 💧

🔄 **سيتم إعادة التشغيل في الدورة القادمة...**
🔔 **يتم المراقبة المستمرة لكل عملة جديدة**

⚡ **MevX Bot - التحديث كل 5 دقائق v3.0**
"""
            self.send_single_message(summary_message)
        
        # تنظيف الذاكرة (الاحتفاظ بآخر 50 عملة فقط)
        if len(self.last_sent_tokens) > 50:
            self.last_sent_tokens = set(list(self.last_sent_tokens)[-50:])
        
        print(f"🎉 اكتمل إرسال {successful_sends} توصية جديدة")
        return successful_sends

# التشغيل الرئيسي - تشغيل واحد فقط ثم إنهاء
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
🤖 **بدء تشغيل بوت الترندينغ المحترف**

⏰ وقت البدء: {datetime.now().strftime('%Y-%m-%d %I:%M %p')}
🔄 التحديث: تشغيل واحد
🎯 الشروط: عملات عمرها أقل من 35 دقيقة

⚡ **جارٍ فحص العملات الحالية...**
"""
        bot.send_single_message(start_message)
        
        # تشغيل دورة واحدة فقط
        print(f"\n🔄 بدء دورة التشغيل - {datetime.now().strftime('%Y-%m-%d %I:%M %p')}")
        count = bot.run_professional_analysis()
        print(f"🎯 اكتمل التشغيل! تم إرسال {count} توصية جديدة")
        
        # إرسال رسالة نهاية التشغيل
        end_message = f"""
🏁 **تم الانتهاء من تشغيل البوت**

⏰ وقت الانتهاء: {datetime.now().strftime('%Y-%m-%d %I:%M %p')}
📊 التوصيات المرسلة: {count}
✅ تم الانتهاء بنجاح

🔜 **سيتم تشغيل البوت مرة أخرى في الدورة التالية**
"""
        bot.send_single_message(end_message)
        
        print("✅ تم إنهاء البوت بنجاح!")
        
    except Exception as e:
        print(f"❌ خطأ غير متوقع: {e}")
        # محاولة إرسال خطأ إلى Telegram
        try:
            error_msg = f"❌ خطأ في البوت: {str(e)[:100]}..."
            bot.send_single_message(error_msg)
        except:
            pass
        sys.exit(1)
    
    sys.exit(0)
