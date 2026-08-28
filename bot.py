import logging
import asyncio
import random
import os
import json
from telethon import TelegramClient, events
from telethon.sessions import StringSession
from telethon.tl.types import ReplyKeyboardMarkup, KeyboardButton
from telethon.errors import SessionPasswordNeededError, PhoneCodeInvalidError
from telethon.tl.functions.account import UpdateProfileRequest
from telethon.tl.functions.photos import UploadProfilePhotoRequest, DeletePhotosRequest
import telethon.tl.functions.users

# --- CẤU HÌNH API & BOT ---
API_ID = 39485214
API_HASH = "cd3c7822f740b7b7af660de3cb1c9f9d"
BOT_TOKEN = "8704592597:AAEK_FoX078pKAYtFqSoPGLINMEf1Y2QakQ"
ADMIN_ID = 7907990385

# Lưu trữ trạng thái hệ thống
active_user_clients = {}
active_tasks = {}
autoclear_status = {}
group_autodelete_status = {}
admin_list = {ADMIN_ID}
is_admin_locked = False

# --- KHO NGÔN WAR ĐẦY ĐỦ ---
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
    if user_id not in active_user_clients:
        await event.respond("⛔ Bạn chưa đăng nhập! Vui lòng bấm nút Login bên dưới hoặc gõ `.login` để xác thực.")
        return None
    
    user_client = active_user_clients[user_id]["client"]
    if not await user_client.is_user_authorized():
        await event.respond("⚠️ Phiên đăng nhập đã hết hạn. Vui lòng đăng nhập lại.")
        return None
    return user_client


# ================= GIAO DIỆN /START (ĐÃ FIX AN TOÀN) =================

@bot.on(events.NewMessage(pattern=r'/start'))
async def send_welcome(event):
    try:
        admin_status_text = "🔴 Đang Khóa" if is_admin_locked else "🟢 Đang Mở"
        keyboard = ReplyKeyboardMarkup([
            [KeyboardButton(text="📱 Login (Chia sẻ số điện thoại)", request_phone=True)],
            [KeyboardButton(text="📜 Xem danh sách lệnh")]
        ], resize=True)

        text_msg = (
            "🔥 **Hot War 2026**\n\n"
            "• `/war` → Spam war liên tục tốc độ 0.1s kèm tag ẩn (Gõ /stop để dừng)\n"
            "• `/spam [nội dung]` → Spam văn bản tùy chỉnh tốc độ 0.1s/tin\n"
            "• `/sptru` → Spam tốc độ 1s/tin\n"
            "• `/voice [nội dung]` → Chuyển văn bản thành giọng nói (Voice)\n"
            "• `/fake` → Bật chế độ giả lập (Fake)\n"
            "• `/diefake` → Tắt chế độ giả lập (Die Fake)\n"
            "• `/aotuclear` → Bật chế độ tự động xóa tin nhắn\n"
            "• `/stop` → Dừng toàn bộ quá trình spam/war\n\n"
            "👑 **QUẢN TRỊ NHÓM**\n"
            "• `/aotudelete` → Tự động xóa tin nhắn trong nhóm\n"
            "• `/undelete` → Tắt tự động xóa tin nhắn\n\n"
            f"🔐 **QUẢN TRỊ VIÊN (ADMIN)** - Trạng thái: {admin_status_text}\n"
            "• `/tb [nội dung]` → Gửi thông báo đến toàn bộ người dùng\n"
            "• `/adm [uid]` → Thêm Admin mới\n"
            "• `/token` → Quản lý tài khoản đăng nhập\n"
            "• `/lockadmin` → Bật/Tắt khóa tính năng admin\n\n"
            "👉 **Bước đầu tiên:** Bấm nút **Login** bên dưới để chia sẻ số điện thoại xác thực."
        )

        await event.respond(text_msg, buttons=keyboard, parse_mode='md')
    except Exception as e:
        # Dự phòng nếu lỗi cú pháp markdown hoặc bàn phím
        try:
            await event.respond("🔥 **Hot War 2026**\nBot đã sẵn sàng! Gõ `.login` để đăng nhập.")
        except:
            pass

@bot.on(events.NewMessage(pattern=r'📜 Xem danh sách lệnh'))
async def view_commands(event):
    await event.respond(
        "📋 **HƯỚNG DẪN SỬ DỤNG LỆNH:**\n"
        "1. Xác thực tài khoản bằng cách bấm nút `Login` hoặc gõ `.login`.\n"
        "2. Sau khi đăng nhập thành công, bạn có thể dùng các lệnh `/war`, `/spam`, `/fake` trực tiếp."
    )


# ================= TÍNH NĂNG ADMIN & BẢO MẬT =================

def check_admin(user_id):
    if is_admin_locked and user_id != ADMIN_ID:
        return False
    return user_id in admin_list

@bot.on(events.NewMessage(pattern=r'/lockadmin'))
async def toggle_lock_admin(event):
    global is_admin_locked
    if event.sender_id != ADMIN_ID:
        await event.respond("❌ Lệnh này chỉ dành riêng cho Chủ Nhân tối cao!")
        return
    
    is_admin_locked = not is_admin_locked
    status = "🔴 Đã Khóa" if is_admin_locked else "🟢 Đã Mở"
    await event.respond(f"🔒 Trạng thái tính năng Admin hiện tại: **{status}**")

@bot.on(events.NewMessage(pattern=r'/tb (.+)'))
async def admin_broadcast(event):
    if not check_admin(event.sender_id):
        await event.respond("❌ Bạn không có quyền sử dụng lệnh này!")
        return
    
    content = event.pattern_match.group(1)
    count = 0
    for uid in active_user_clients.keys():
        try:
            await bot.send_message(uid, f"📢 **THÔNG BÁO TỪ ADMIN:**\n\n{content}")
            count += 1
        except Exception:
            pass
    await event.respond(f"✅ Đã gửi thông báo thành công tới `{count}` người dùng!")

@bot.on(events.NewMessage(pattern=r'/adm (.+)'))
async def admin_add(event):
    if event.sender_id != ADMIN_ID:
        await event.respond("❌ Chỉ Chủ Nhân mới có quyền thêm Admin mới!")
        return
    
    target = event.pattern_match.group(1).strip()
    try:
        if target.isdigit():
            new_admin_id = int(target)
            admin_list.add(new_admin_id)
            await event.respond(f"👑 Đã thêm ID `{new_admin_id}` vào danh sách Quản Trị Viên!")
        else:
            await event.respond("❌ Vui lòng nhập đúng dạng UID số (Ví dụ: `/adm 123456789`)")
    except Exception as e:
        await event.respond(f"❌ Lỗi: {e}")

@bot.on(events.NewMessage(pattern=r'/token'))
async def admin_token_management(event):
    if not check_admin(event.sender_id):
        await event.respond("❌ Bạn không có quyền truy cập quản lý token!")
        return
    
    total = len(active_user_clients)
    msg = f"📊 **QUẢN LÝ TÀI KHOẢN ĐĂNG NHẬP:**\n- Tổng số phiên active: `{total}`\n\n"
    for uid in active_user_clients.keys():
        msg += f"• User ID: `{uid}`\n"
    await event.respond(msg)


# ================= QUẢN LÝ ĐĂNG NHẬP (MEMBER) =================

@bot.on(events.NewMessage(pattern=r'\.login'))
async def start_login_command(event):
    phone_button = [[KeyboardButton(text="📱 Chia sẻ số điện thoại để đăng nhập", request_phone=True)]]
    keyboard = ReplyKeyboardMarkup(phone_button, resize=True, one_time_keyboard=True)
    await event.respond("👉 Bấm vào nút bên dưới để chia sẻ số điện thoại:", buttons=keyboard)

@bot.on(events.NewMessage(func=lambda e: e.message.contact))
async def received_phone(event):
    user_id = event.sender_id
    contact = event.message.contact
    if contact.user_id != user_id:
        await event.respond("❌ Vui lòng chia sẻ đúng số điện thoại của chính bạn!")
        return

    phone_number = contact.phone_number
    if not phone_number.startswith('+'):
        phone_number = '+' + phone_number

    await event.respond(f"⏳ Đang gửi mã OTP tới **{phone_number}**...")

    try:
        user_client = TelegramClient(StringSession(), API_ID, API_HASH)
        await user_client.connect()
        sent_code = await user_client.send_code_request(phone_number)
        
        active_user_clients[user_id] = {
            "client": user_client,
            "phone": phone_number,
            "phone_code_hash": sent_code.phone_code_hash
        }

        await event.respond(
            "✅ Đã gửi mã OTP thành công!\n\n"
            "📩 Hãy nhập mã OTP theo cú pháp:\n"
            "`/code [mã_otp]`\n"
            "*(Ví dụ: `/code 12345`)*"
        )
    except Exception as e:
        await event.respond(f"❌ Lỗi gửi mã: {str(e)}")

@bot.on(events.NewMessage(pattern=r'/code (.+)'))
async def verify_code(event):
    user_id = event.sender_id
    code = event.pattern_match.group(1).strip()

    if user_id not in active_user_clients:
        await event.respond("⚠️ Bạn chưa bấm Login hoặc chưa chia sẻ số điện thoại!")
        return

    user_data = active_user_clients[user_id]
    user_client = user_data["client"]
    phone = user_data["phone"]
    phone_code_hash = user_data["phone_code_hash"]

    try:
        await user_client.sign_in(phone=phone, code=code, phone_code_hash=phone_code_hash)
        await event.respond("🎉 **ĐĂNG NHẬP THÀNH CÔNG!** Toàn bộ tính năng đã được mở khóa.")
    except SessionPasswordNeededError:
        await event.respond("🔒 Tài khoản bật **2FA**. Vui lòng nhập mật khẩu bằng cú pháp:\n`/2fa [mật_khẩu]`")
    except PhoneCodeInvalidError:
        await event.respond("❌ Mã OTP không chính xác!")
    except Exception as e:
        await event.respond(f"❌ Lỗi đăng nhập: {str(e)}")

@bot.on(events.NewMessage(pattern=r'/2fa (.+)'))
async def verify_2fa(event):
    user_id = event.sender_id
    password = event.pattern_match.group(1).strip()

    if user_id not in active_user_clients:
        await event.respond("⚠️ Phiên làm việc không tồn tại.")
        return

    user_client = active_user_clients[user_id]["client"]
    try:
        await user_client.sign_in(password=password)
        await event.respond("🎉 **Xác thực 2FA thành công! Bot đã sẵn sàng.**")
    except Exception as e:
        await event.respond(f"❌ Mật khẩu 2FA không chính xác: {str(e)}")


# ================= TÍNH NĂNG CHÍNH (WAR, SPAM, FAKE, VOICE...) =================

@bot.on(events.NewMessage(pattern=r'/war'))
async def user_war(event):
    user_client = await get_authorized_client(event)
    if not user_client: return

    chat_id = event.chat_id
    active_tasks[chat_id] = True
    reply_to = event.get_reply_message().id if event.is_reply else None
    
    while active_tasks.get(chat_id, False):
        try:
            msg = random.choice(WAR_WORDS) + " " + create_hidden_tag()
            sent = await user_client.send_message(chat_id, msg, parse_mode='md', reply_to=reply_to)
            if autoclear_status.get(chat_id, False):
                await asyncio.sleep(2)
                await sent.delete()
            await asyncio.sleep(0.1)
        except Exception:
            await asyncio.sleep(0.2)

@bot.on(events.NewMessage(pattern=r'/spam (.+)'))
async def user_spam(event):
    user_client = await get_authorized_client(event)
    if not user_client: return

    chat_id = event.chat_id
    spam_text = event.pattern_match.group(1)
    active_tasks[chat_id] = True
    
    while active_tasks.get(chat_id, False):
        try:
            msg = spam_text + " " + create_hidden_tag()
            sent = await user_client.send_message(chat_id, msg, parse_mode='md')
            if autoclear_status.get(chat_id, False):
                await asyncio.sleep(2)
                await sent.delete()
            await asyncio.sleep(0.1)
        except Exception:
            await asyncio.sleep(0.2)

@bot.on(events.NewMessage(pattern=r'/sptru'))
async def user_sptru(event):
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

@bot.on(events.NewMessage(pattern=r'/voice (.+)'))
async def user_voice(event):
    user_client = await get_authorized_client(event)
    if not user_client: return
    text = event.pattern_match.group(1)
    await event.respond(f"🎙️ [Mô phỏng Voice]: {text}")

@bot.on(events.NewMessage(pattern=r'/fake'))
async def user_fake(event):
    user_client = await get_authorized_client(event)
    if not user_client: return

    if not event.is_reply:
        await event.respond("❌ Vui lòng reply vào tin nhắn của người bạn muốn fake thông tin!")
        return
    try:
        reply_msg = await event.get_reply_message()
        target_user = await reply_msg.get_sender()
        if not target_user: return

        me = await user_client.get_me()
        full_me = await user_client(telethon.tl.functions.users.GetFullUserRequest(id=me.id))
        
        orig_data = {"first_name": me.first_name or "", "last_name": me.last_name or "", "about": full_me.full_user.about or ""}
        active_user_clients[event.sender_id]["orig_profile"] = orig_data

        target_full = await user_client(telethon.tl.functions.users.GetFullUserRequest(id=target_user.id))
        await user_client(UpdateProfileRequest(first_name=target_user.first_name or "User", last_name=target_user.last_name or "", about=target_full.full_user.about or ""))
        
        photo_path = await user_client.download_profile_photo(target_user, file="temp_avatar.jpg")
        if photo_path:
            uploaded_photo = await user_client.upload_file(photo_path)
            await user_client(UploadProfilePhotoRequest(file=uploaded_photo))
            if os.path.exists(photo_path): os.remove(photo_path)

        await event.respond("🎭 [SUCCESS] Đã bật chế độ giả lập (Fake) thành công!")
    except Exception as e:
        await event.respond(f"❌ Lỗi: {e}")

@bot.on(events.NewMessage(pattern=r'/diefake'))
async def user_diefake(event):
    user_client = await get_authorized_client(event)
    if not user_client: return

    user_data = active_user_clients.get(event.sender_id, {})
    if "orig_profile" not in user_data:
        await event.respond("⚠️ Không tìm thấy dữ liệu gốc để tắt fake!")
        return
    try:
        orig_data = user_data["orig_profile"]
        await user_client(UpdateProfileRequest(first_name=orig_data["first_name"], last_name=orig_data["last_name"], about=orig_data["about"]))
        photos = await user_client.get_profile_photos('me')
        if photos: await user_client(DeletePhotosRequest(id=[photos[0]]))
        await event.respond("🛡️ Đã tắt chế độ giả lập (Die Fake) thành công!")
    except Exception as e:
        await event.respond(f"❌ Lỗi: {e}")

@bot.on(events.NewMessage(pattern=r'/aotuclear'))
async def user_aotuclear(event):
    user_client = await get_authorized_client(event)
    if not user_client: return
    autoclear_status[event.chat_id] = True
    await event.respond("🧹 Đã bật chế độ tự động xóa tin nhắn cá nhân!")

@bot.on(events.NewMessage(pattern=r'/stop'))
async def user_stop(event):
    user_client = await get_authorized_client(event)
    if not user_client: return
    chat_id = event.chat_id
    active_tasks[chat_id] = False
    autoclear_status[chat_id] = False
    group_autodelete_status[chat_id] = False
    await event.respond("🛑 Đã dừng toàn bộ quá trình spam/war và reset trạng thái!")


# ================= QUẢN TRỊ NHÓM =================

@bot.on(events.NewMessage(pattern=r'/aotudelete'))
async def group_autodelete(event):
    if not event.is_group:
        await event.respond("❌ Lệnh này chỉ dùng được trong nhóm (Group)!")
        return
    group_autodelete_status[event.chat_id] = True
    await event.respond("👑 Đã bật chế độ tự động xóa tin nhắn trong nhóm!")

@bot.on(events.NewMessage(pattern=r'/undelete'))
async def group_undelete(event):
    if not event.is_group:
        await event.respond("❌ Lệnh này chỉ dùng được trong nhóm!")
        return
    group_autodelete_status[event.chat_id] = False
    await event.respond("👑 Đã tắt tự động xóa tin nhắn trong nhóm.")

@bot.on(events.NewMessage())
async def handle_group_autodelete(event):
    if event.is_group and group_autodelete_status.get(event.chat_id, False):
        if event.sender_id != ADMIN_ID:
            try:
                await asyncio.sleep(3)
                await event.delete()
            except Exception:
                pass


async def main():
    print(f"🔥 Bot Hot War 2026 đang chạy! ID Admin cố định: {ADMIN_ID}")
    await bot.start(bot_token=BOT_TOKEN)
    await bot.run_until_disconnected()

if __name__ == '__main__':
    asyncio.run(main())
