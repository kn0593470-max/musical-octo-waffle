import logging
import asyncio
import random
import os
import json
from telethon import TelegramClient, events
from telethon.tl.functions.account import UpdateProfileRequest
from telethon.tl.functions.photos import UploadProfilePhotoRequest, DeletePhotosRequest
import telethon.tl.functions.users

# --- CẤU HÌNH API ĐÃ LẤY CỦA BẠN ---
API_ID = 39485214
API_HASH = "cd3c7822f740b7b7af660de3cb1c9f9d"

# --- KHO NGÔN WAR ĐẦY ĐỦ KÈM TAG ẨN ---
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

logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)

client = TelegramClient('dnamky_session', API_ID, API_HASH)
active_tasks = {}
autoclear_status = {}
PROFILE_FILE = "original_profile.json"

def create_hidden_tag(user_id=1531685790491480419):
    return f"[\u200b](tg://user?id={user_id})"

# 1. Lệnh .war
@client.on(events.NewMessage(pattern=r'\.war', outgoing=True))
async def user_war(event):
    chat_id = event.chat_id
    active_tasks[chat_id] = True
    
    reply_to = None
    if event.is_reply:
        reply_msg = await event.get_reply_message()
        reply_to = reply_msg.id
        await event.edit("⚔️ [USERBOT] Bắt đầu War tốc độ cao (0.1s/tin) nhắm vào mục tiêu được Reply!")
    else:
        await event.edit("⚔️ [USERBOT] Đã kích hoạt chiến dịch War tốc độ 0.1s toàn khung chat!")
    
    while active_tasks.get(chat_id, False):
        try:
            msg = random.choice(WAR_WORDS) + " " + create_hidden_tag()
            sent = await client.send_message(chat_id, msg, parse_mode='md', reply_to=reply_to)
            
            if autoclear_status.get(chat_id, False):
                await asyncio.sleep(2)
                await sent.delete()
                
            await asyncio.sleep(0.1)
        except Exception:
            await asyncio.sleep(0.2)

# 2. Lệnh .spam
@client.on(events.NewMessage(pattern=r'\.spam (.+)', outgoing=True))
async def user_spam(event):
    chat_id = event.chat_id
    spam_text = event.pattern_match.group(1)
    active_tasks[chat_id] = True
    await event.edit(f"🚀 [USERBOT] Bắt đầu spam: '{spam_text}' (0.1s/tin)")
    
    while active_tasks.get(chat_id, False):
        try:
            msg = spam_text + " " + create_hidden_tag()
            sent = await client.send_message(chat_id, msg, parse_mode='md')
            if autoclear_status.get(chat_id, False):
                await asyncio.sleep(2)
                await sent.delete()
            await asyncio.sleep(0.1)
        except Exception:
            await asyncio.sleep(0.2)

# 3. Lệnh .sptru
@client.on(events.NewMessage(pattern=r'\.sptru (.+)', outgoing=True))
async def user_sptru(event):
    chat_id = event.chat_id
    spam_text = event.pattern_match.group(1)
    active_tasks[chat_id] = True
    await event.edit(f"🐢 [USERBOT] Bắt đầu spam tốc độ chậm: '{spam_text}' (1s/tin)")
    
    while active_tasks.get(chat_id, False):
        try:
            msg = spam_text + " " + create_hidden_tag()
            await client.send_message(chat_id, msg, parse_mode='md')
            await asyncio.sleep(1.0)
        except Exception:
            await asyncio.sleep(1.0)

# 4. Lệnh .fake (Tự động lưu gốc vào file và đổi thông tin theo người được reply)
@client.on(events.NewMessage(pattern=r'\.fake', outgoing=True))
async def user_fake(event):
    if not event.is_reply:
        await event.edit("❌ Vui lòng reply vào tin nhắn của người bạn muốn fake thông tin!")
        return
    
    try:
        await event.edit("🔄 Đang tiến hành lưu thông tin gốc và fake profile...")
        reply_msg = await event.get_reply_message()
        target_user = await reply_msg.get_sender()
        
        if not target_user:
            await event.edit("❌ Không thể lấy thông tin người dùng này!")
            return

        # Nếu chưa có file lưu thông tin gốc, tiến hành lưu lại ngay bây giờ
        if not os.path.exists(PROFILE_FILE):
            me = await client.get_me()
            full_me = await client(telethon.tl.functions.users.GetFullUserRequest(id=me.id))
            
            orig_data = {
                "first_name": me.first_name or "",
                "last_name": me.last_name or "",
                "about": full_me.full_user.about or ""
            }
            with open(PROFILE_FILE, "w", encoding="utf-8") as f:
                json.dump(orig_data, f, ensure_ascii=False, indent=4)

        # Lấy thông tin chi tiết mục tiêu cần fake
        target_full = await client(telethon.tl.functions.users.GetFullUserRequest(id=target_user.id))
        target_about = target_full.full_user.about or ""
        target_firstname = target_user.first_name or "User"
        target_lastname = target_user.last_name or ""

        # 1. Đổi tên và tiểu sử sang nạn nhân
        await client(UpdateProfileRequest(
            first_name=target_firstname,
            last_name=target_lastname,
            about=target_about
        ))

        # 2. Đổi avatar sang nạn nhân
        photo_path = await client.download_profile_photo(target_user, file="temp_avatar.jpg")
        if photo_path:
            uploaded_photo = await client.upload_file(photo_path)
            await client(UploadProfilePhotoRequest(file=uploaded_photo))
            if os.path.exists(photo_path):
                os.remove(photo_path)

        await event.edit(f"🎭 [SUCCESS] Đã fake thành công thông tin của **{target_firstname}**!")

    except Exception as e:
        await event.edit(f"❌ Lỗi khi fake: {e}")

# 5. Lệnh .diefake / .die fake (Đọc file lưu gốc để khôi phục hoàn toàn)
@client.on(events.NewMessage(pattern=r'\.(?:die\s*fake|diefake)', outgoing=True))
async def user_diefake(event):
    if not os.path.exists(PROFILE_FILE):
        await event.edit("⚠️ Không tìm thấy file dữ liệu gốc! Có thể bạn chưa dùng lệnh `.fake` lần nào.")
        return
    
    try:
        await event.edit("🔄 Đang đọc dữ liệu gốc và khôi phục tài khoản...")
        
        with open(PROFILE_FILE, "r", encoding="utf-8") as f:
            orig_data = json.load(f)
        
        # 1. Khôi phục tên và tiểu sử gốc
        await client(UpdateProfileRequest(
            first_name=orig_data["first_name"],
            last_name=orig_data["last_name"],
            about=orig_data["about"]
        ))
        
        # 2. Xóa avatar giả để trả về trạng thái cũ
        photos = await client.get_profile_photos('me')
        if photos:
            await client(DeletePhotosRequest(id=[photos[0]]))

        await event.edit("🛡️ Đã khôi phục lại tài khoản gốc hoàn toàn thành công!")
    except Exception as e:
        await event.edit(f>
