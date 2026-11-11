/* EVA Video Studio — website language (English default, Simplified Chinese). One shared dictionary for every page:
   English source text → 简体中文. Pages stay English in the HTML (URLs and SEO unchanged); in Chinese mode this script
   translates the static text after load, and app.js / templates.js ask I18N.t() for the text they create.
   Never translated: template IDs, user uploads, video titles, subtitles, emails, amounts and billing data.
   The choice is kept in localStorage ("eva:lang"), so it survives navigation, reloads and the sign-in round trip;
   ?lang=zh / ?lang=en sets it too. */
(function () {
  const KEY = "eva:lang";
  const pick = () => {
    try {
      const q = new URLSearchParams(location.search).get("lang");
      if (q === "zh" || q === "en") localStorage.setItem(KEY, q);
      return localStorage.getItem(KEY) === "zh" ? "zh" : "en";
    } catch (e) { return "en"; }
  };
  const lang = pick();

  const ZH = {
    // navigation, header, footer, account menu
    "How it works": "使用方法", "Templates": "模板", "Make a video": "制作视频", "Pricing": "价格", "My Videos": "我的视频",
    "Sign in": "登录", "Account menu": "账户菜单", "Your account": "我的账户", "My Account": "我的账户", "Credits & Billing": "点数与账单",
    "Sign Out": "退出登录", "Sign out": "退出登录", "Balance unavailable right now": "暂时无法显示余额",
    "{credits} credits · {free} of {limit} free previews left": "{credits} 点 · 免费预览剩余 {free}/{limit} 次",
    "Terms, privacy and refunds": "条款、隐私与退款", "Language": "语言",
    // homepage hero
    "Upload a talking-head video from your phone. We add captions, motion cards and music, then cut it for Reels, TikTok or YouTube.":
      "上传手机拍摄的口播视频，我们自动添加字幕、动态卡片和音乐，并剪成适合 Reels、抖音/TikTok 或 YouTube 的成片。",
    "Upload a video": "上传视频", "Vertical · 9:16": "竖屏 · 9:16", "Horizontal · 16:9": "横屏 · 16:9",
    "Drag a handle to compare each raw upload with its edit.": "拖动中间的滑块，对比原始视频和剪辑后的效果。",
    "Raw": "原片", "Edited": "成片", "Sound off": "声音关", "Sound on": "声音开", "Raw upload": "原始视频", "Edited video": "剪辑后的视频",
    "Move the comparison divider": "移动对比分割线", "Style Showcase": "风格展示", "Montage of EVA editing styles": "EVA 多种剪辑风格混剪",
    "Left: a raw phone clip. Right: a montage of different EVA editing styles. Drag the handle to compare.": "左侧：手机拍摄的原片。右侧：EVA 多种剪辑风格的混剪。拖动滑块进行对比。",
    "Some styles shown are Preview Only and not yet available for online rendering.": "部分展示的风格为“仅预览”，暂不支持在线生成。", "{title} example coming soon": "{title} 示例即将上线",
    // How EVA works
    "How EVA works": "EVA 如何工作", "Three steps from your phone video to a finished, edited short.": "三步，把手机视频变成剪辑好的短视频成片。",
    "Upload a video": "上传视频", "MP4 or MOV, up to 30 seconds, with you speaking.": "MP4 或 MOV，最长 30 秒，画面中是你在讲话。",
    "Choose a template": "选择模板", "Pick a style, or let us choose for you.": "挑一个风格，或让我们帮你选。",
    "Generate your video": "生成视频", "A free preview in a few minutes, then export in full HD.": "几分钟内得到免费预览，满意后导出全高清版本。",
    "Your real footage": "保留你的真实画面", "Captions, motion cards and music added to your own clip": "在你自己的视频上添加字幕、动态卡片和音乐",
    "25 styles, growing": "25 种风格，持续增加", "5 ready to use today, more on the way": "其中 5 种现已可用，更多即将推出",
    "Ready to post": "直接可发布", "1080p for Reels, TikTok, Shorts and YouTube": "1080p，适用于 Reels、抖音/TikTok、Shorts 和 YouTube",
    "25 video styles": "25 种视频风格", "5 ready to use now": "5 种现已可用", "Template category": "模板分类",
    "All": "全部", "Ready now": "现可使用", "Explainers": "讲解", "Education": "教育", "Tech & AI": "科技与 AI", "Social": "社媒",
    "Ready": "可用", "Preview": "预览", "Ready to use": "可直接使用", "Explore all templates": "查看全部模板",
    // studio (upload flow)
    "Make your video": "制作你的视频", "MP4 or MOV, up to 30 seconds and 200 MB, with you speaking. The preview is free.": "MP4 或 MOV，最长 30 秒、最大 200 MB，画面中是你在讲话。预览免费。",
    "Choose a video or drop it here": "选择视频，或拖到这里", "Portrait or landscape, straight from your phone": "竖屏或横屏都可以，直接用手机拍的就行",
    "Format": "画幅", "9:16 for Reels, TikTok, Shorts": "9:16 竖屏：Reels、抖音/TikTok、Shorts", "16:9 for YouTube": "16:9 横屏：YouTube",
    "Visual style": "视觉风格", "pick one, several, or let us choose": "可选一个、多个，或让我们来选", "Music": "音乐",
    "original tracks, licensed for your video": "原创曲目，已授权用于你的视频", "AI Auto Mix": "AI 自动配乐", "I'll choose tracks": "我自己选曲目", "No music": "不加音乐",
    "Choose up to three. With more than one, each part of your video gets the next track.": "最多选 3 首。选多首时，视频的每一段依次使用下一首。",
    "Make my free preview": "生成我的免费预览", "Let us choose": "让我们来选", "Browse all templates →": "浏览全部模板 →",
    "Listen": "试听", "Stop": "停止", "Full preview": "完整预览", "Close": "关闭", "Template preview": "模板预览",
    "Play the {name} demo": "播放 {name} 示例", "{name} template": "{name} 模板", "{ar} preview coming soon": "{ar} 预览即将上线", "▶ 5 s": "▶ 5 秒",
    "Choose up to three tracks.": "最多选择 3 首曲目。",
    "Use the first {n}": "只用前 {n} 种", "Too many styles for this clip. Choose fewer, then try again.": "这个视频放不下这么多风格。请少选几种后再试。",
    "Your {d}-second clip fits up to {n} styles (about {m} s each). You picked {k}. Choose fewer styles, or upload a longer clip.": "你的 {d} 秒视频最多适合 {n} 种风格（每种约 {m} 秒），你选了 {k} 种。请少选几种，或上传更长的视频。",
    "Your first 3 previews are free. Sign in when you're ready.": "前 3 次预览免费。准备好后再登录即可。",
    "This preview is free ({free} of 3 free previews left). Full HD export: {hd} credits.": "本次预览免费（免费预览剩余 {free}/3 次）。全高清导出：{hd} 点。",
    "This preview costs {cost} credits (you have {credits}). Full HD export: {hd} credits.": "本次预览需 {cost} 点（你有 {credits} 点）。全高清导出：{hd} 点。",
    "This preview costs {cost} credits and you have {credits}. Top up: $9.99 = 100 credits.": "本次预览需 {cost} 点，你有 {credits} 点。充值：$9.99 = 100 点。",
    "Make preview · {cost} credits": "生成预览 · {cost} 点",
    "Choose a video first.": "请先选择一个视频。", "Please upload an MP4 or MOV video.": "请上传 MP4 或 MOV 视频。",
    "This video is larger than 200 MB. Trim or compress it, then try again.": "视频超过 200 MB。请剪短或压缩后再试。",
    "This video is {n} seconds long. The limit is 30 seconds.": "这个视频长 {n} 秒，上限为 30 秒。",
    "Choose a visual style, or Let us choose.": "请选择一种视觉风格，或选择“让我们来选”。",
    "Choose at least one track, or pick AI Auto Mix.": "请至少选一首曲目，或选择“AI 自动配乐”。",
    "Sign in with your email to make your preview. Your first 3 previews are free.": "用邮箱登录即可生成预览。前 3 次预览免费。",
    "Uploading…": "上传中…", "Uploading… {pct}%": "上传中… {pct}%", "The upload was interrupted. Please try again.": "上传中断，请重试。",
    "Starting your preview…": "正在开始生成预览…",
    // sign-in
    "Email": "邮箱", "Email me a sign-in link": "给我发送登录链接", "Enter your email address.": "请输入邮箱地址。",
    "Check your inbox: the link signs you in and brings you back here.": "请查看邮箱：点击链接即可登录并回到这里。",
    "Sign in with your email to save your videos and get 3 free previews.": "用邮箱登录，保存你的视频并获得 3 次免费预览。",
    "Sign-in is not available right now.": "登录功能暂时不可用。", "Please sign in.": "请先登录。",
    // top-up
    "Top up $9.99 · 100 credits": "充值 $9.99 · 100 点",
    "Credits pay for previews after your free ones (12–15 credits) and full HD exports (38–52 credits). Secure checkout by Stripe.": "免费次数用完后，预览需 12–15 点，全高清导出需 38–52 点。由 Stripe 提供安全支付。",
    // video page
    "Your preview appears here": "预览将显示在这里", "Loading your video…": "正在加载你的视频…", "Video progress": "视频进度",
    "Saved privately in My Videos. Previews and your original upload are kept for 30 days, HD exports for 90 days.": "已私密保存在“我的视频”。预览和原始视频保留 30 天，高清导出保留 90 天。",
    "Cancel": "取消", "Starting…": "正在开始…", "Sign in to see this video": "登录后查看这个视频", "We can't find this video": "找不到这个视频",
    "It may have been deleted or have expired.": "它可能已被删除或已过期。", "Connection problem. Retrying…": "网络连接有问题，正在重试…",
    "Payment received. Your balance: {credits} credits.": "已收到付款。你的余额：{credits} 点。", "Checkout was canceled. You haven't been charged.": "已取消付款，没有扣费。",
    " Kept until {date}.": " 保留至 {date}。", "Rendering your HD video": "正在渲染高清视频", "Making preview {n}": "正在生成预览 {n}",
    "{title} · {tpl}. This usually takes a few minutes; you can leave and come back from My Videos.": "{title} · {tpl}。通常需要几分钟，你可以先离开，稍后从“我的视频”回来查看。",
    "{title} · {tpl}. This usually takes 2–4 minutes; you can leave and come back from My Videos.": "{title} · {tpl}。通常需要 2–4 分钟，你可以先离开，稍后从“我的视频”回来查看。",
    "This is taking longer than usual. If it can't finish, nothing is charged.": "这次比平时慢一些。如果无法完成，不会扣费。",
    "rendering": "渲染中", "ready": "已完成", "Rendering in full HD…": "正在全高清渲染…", "Rendering your preview…": "正在渲染你的预览…",
    "This render was canceled": "本次渲染已取消", "This render didn't finish": "本次渲染未完成",
    "It didn't pass our quality checks. ": "未通过我们的质量检查。", "Something went wrong on our side. ": "我们这边出了问题。",
    "Nothing was charged: free previews and credits were returned.": "没有扣费：免费次数和点数均已退回。", "Not available": "不可用", "Back to My Videos": "返回我的视频",
    "Your HD video is ready": "你的高清视频已完成",
    "{title} · version {n} · {tpl}. Full HD {w}×{h}.{until} Downloading again is free.": "{title} · 版本 {n} · {tpl}。全高清 {w}×{h}。{until}再次下载免费。",
    "Preview {n} is ready": "预览 {n} 已完成", "{title} · {tpl}. Full length, 720p, with a watermark.{until}": "{title} · {tpl}。完整长度，720p，带水印。{until}",
    "Loading…": "加载中…", "Download HD": "下载高清版", "Play HD": "播放高清版", "HD export in progress…": "高清导出进行中…",
    "Export this version in full 1080p for {cost} credits? You have {credits}; {left} will be left. If the export fails, the credits come back.": "用 {cost} 点把这个版本导出为全高清 1080p？你有 {credits} 点，导出后剩 {left} 点。如果导出失败，点数会退回。",
    "Exporting costs {cost} credits and you have {credits}.": "导出需要 {cost} 点，你有 {credits} 点。", "Export for {cost} credits": "用 {cost} 点导出", "Top up first": "先充值",
    "Exporting costs {cost} credits and you have {credits}. Top up to continue.": "导出需要 {cost} 点，你有 {credits} 点。请充值后继续。",
    "Export HD · {cost} credits": "导出高清 · {cost} 点",
    "Make a new version from the same upload and settings? It's free ({free} of 3 free previews left). Your current versions stay in My Videos.": "用同一个视频和设置生成新版本？本次免费（免费预览剩余 {free}/3 次）。现有版本会保留在“我的视频”。",
    "Make a new version from the same upload and settings for {cost} credits? You have {credits}. Your current versions stay saved, and if it fails the credits come back.": "用同一个视频和设置生成新版本，需要 {cost} 点？你有 {credits} 点。现有版本会保留；如果失败，点数会退回。",
    "Yes, make a new version": "好的，生成新版本", "New version": "新版本",
    // My Videos
    "Your created videos are saved here.": "你制作的视频都保存在这里。", "We couldn't load your videos right now.": "暂时无法加载你的视频。", "Try again": "重试",
    "You're signed in, but your videos could not be loaded. Please try again in a moment.": "你已登录，但暂时无法加载视频。请稍后再试。",
    "Sign in to see your saved videos.": "登录后查看已保存的视频。", "Sign in with your email to see your videos. New accounts get 3 free previews.": "用邮箱登录查看你的视频。新账户可获得 3 次免费预览。",
    "Uploaded {date}": "上传于 {date}", " · original kept until {date}": " · 原始视频保留至 {date}", "New version · free": "新版本 · 免费",
    "New version · {cost} credits": "新版本 · {cost} 点", "Make a new version from the same upload and settings? Free ({free} free previews left).": "用同一个视频和设置生成新版本？免费（免费预览剩余 {free} 次）。",
    "Make a new version for {cost} credits? You have {credits}.": "用 {cost} 点生成新版本？你有 {credits} 点。", "Delete": "删除",
    "Delete “{title}” and all its versions? This can't be undone.": "删除“{title}”及其所有版本？此操作无法撤销。", "Open version {n}": "打开版本 {n}",
    "HD": "高清", "Favorite": "收藏", "Version {n}": "版本 {n}", "Preview kept until {date}": "预览保留至 {date}", " · HD until {date}": " · 高清保留至 {date}",
    "Rendering…": "渲染中…", "Nothing was charged": "未扣费", "Play": "播放", "HD rendering…": "高清渲染中…", "Export HD · {cost}": "导出高清 · {cost} 点",
    "Delete version {n}?": "删除版本 {n}？", "Delete version {n} and its HD export?": "删除版本 {n} 及其高清导出？", "Processing": "处理中",
    "Payment received. Your balance is {credits} credits.": "已收到付款。你的余额为 {credits} 点。", "Video": "视频", "Video not found": "找不到视频",
    "← All videos": "← 全部视频", "This video was deleted or isn't in your account.": "这个视频已被删除，或不属于你的账户。",
    "No videos yet. Upload a talking-head clip to make your first preview.": "还没有视频。上传一段口播视频，生成你的第一个预览吧。",
    "({n} video)": "（{n} 个视频）", "({n} videos)": "（{n} 个视频）", "{title}, {dur}": "{title}，{dur}", ", processing": "，处理中",
    "Click again to confirm": "再点一次确认", "queued": "排队中", "running": "处理中", "failed": "失败", "qa failed": "质检未通过", "canceled": "已取消",
    // My Account
    "Loading your account…": "正在加载你的账户…", "Sign in with your email to see your account. New accounts get 3 free previews.": "用邮箱登录查看你的账户。新账户可获得 3 次免费预览。",
    "Optional": "选填", "Display name": "显示名称", "Save": "保存", "Saved.": "已保存。", "Profile": "个人资料",
    "You stay signed in on this device until you sign out.": "在这台设备上会保持登录，直到你退出。",
    "Your balance and history could not be loaded right now. Please try again in a moment.": "暂时无法加载余额和记录，请稍后再试。",
    "Buy {credits} credits · ${price}": "购买 {credits} 点 · ${price}", "credits": "点", "free previews left": "剩余免费预览",
    "Loading history…": "正在加载记录…", "Purchases and charges": "购买与消费记录", "Payment canceled. Nothing was charged.": "已取消付款，没有扣费。",
    "No purchases or charges yet.": "还没有购买或消费记录。", "+{credits} credits": "+{credits} 点", "Free preview": "免费预览", "{credits} credits": "{credits} 点",
    "Charged": "已扣费", "Refunded": "已退回", "In progress": "进行中", "Paid": "已支付", "Granted": "已发放", "Applied": "已生效", "Returned": "已退回",
    "Date": "日期", "Item": "项目", "Amount": "数额", "Status": "状态", "History is unavailable right now.": "暂时无法显示记录。",
    "Credit purchase": "购买点数", "Credit grant": "赠送点数", "Preview (free)": "预览（免费）", "HD export": "高清导出", "Adjustment": "调整",
    // Templates gallery
    "5 ready to use today. More styles are on the way.": "目前 5 种可直接使用，更多风格即将推出。", "Search templates": "搜索模板", "Filter": "筛选",
    "Load more": "加载更多", "Template details": "模板详情", "All templates": "全部模板", "Available now": "现可使用", "Available": "可使用",
    "Preview only": "仅预览", "Coming soon": "即将推出", "Coming soon.": "即将推出。", "Details coming soon.": "详情即将推出。", "Sample frame": "示例画面",
    "Vertical 9:16": "竖屏 9:16", "Horizontal 16:9": "横屏 16:9", "Use template": "使用模板", "Preview coming soon": "预览即将上线",
    "Preview only — not available for rendering yet.": "仅预览，暂不能用于生成视频。", "No templates match. Try another word or filter.": "没有匹配的模板，换个关键词或筛选试试。",
    "The gallery could not be loaded. Please refresh.": "模板库加载失败，请刷新页面。", "{n} templates": "{n} 个模板", "{n} template": "{n} 个模板", " · showing {n}": " · 显示 {n} 个",
    "{name}, {status}. Open details": "{name}，{status}。打开详情", "Play the {ar} preview": "播放 {ar} 预览",
    "Hooks & Openers": "开场钩子", "Explainers & Tutorials": "讲解与教程", "Business & Data": "商业与数据", "Product & Launch": "产品与发布",
    "Storytelling": "故事叙述", "Social & Creator": "社媒与创作者", "Premium & Brand": "高端与品牌", "Real Estate": "房地产",
    "Needs your own footage — coming after launch": "需要你自己的素材，上线后推出", "Needs your own cartoon clips": "需要你自己的卡通素材", "Vertical 9:16 version coming soon": "竖屏 9:16 版本即将推出",
    "Openings, hooks, bold claims, wins": "开场、钩子、大胆观点、成果展示", "Numbers, results, efficiency, comparisons": "数据、成果、效率、对比",
    "Showing real screen recordings and product demos": "展示真实录屏和产品演示", "Pain points, problems, calm explanations, lists": "痛点、问题、平静讲解、清单",
    "Key point, call to action, finale": "重点、行动号召、结尾", "Product reveal": "产品揭晓",
    "Storytelling, milestones, playful transitions (needs your own cartoon clips)": "故事叙述、里程碑、俏皮转场（需要你自己的卡通素材）",
    "Explaining a concept or term, tutorials, analogies": "解释概念或术语、教程、类比", "Channel or series openings, launches, portfolio": "频道或系列开场、发布、作品集",
    "Announcements, milestones, big news, launches": "公告、里程碑、重大消息、发布", "How-to, workflows, tips, features, compatibility, iteration": "操作方法、工作流程、技巧、功能、兼容性、迭代",
    "Stories, look-backs, calling out a problem, opinion pieces": "故事、回顾、指出问题、观点内容", "Tech, AI and product talks, agendas, chapter titles, comparing options": "科技、AI 与产品话题、议程、章节标题、方案对比",
    "Big news, rules or key points, AI and future topics, endings": "重大消息、规则或要点、AI 与未来话题、结尾", "Education, study tips, vocabulary and reading, videos for kids and parents": "教育、学习技巧、词汇与阅读、亲子视频",
    "Fun and playful talks, before-vs-after comparisons, key points, tip lists": "轻松有趣的话题、前后对比、要点、技巧清单", "Tech and AI trends, science topics, how learning works, future outlooks": "科技与 AI 趋势、科学话题、学习原理、未来展望",
    "Bringing in real footage: news clips, product shots, tech and AI news openers": "引入真实素材：新闻片段、产品镜头、科技与 AI 新闻开场",
    "High-energy TikTok / Shorts / Reels pieces, launches, quick tips": "高能量的抖音/TikTok、Shorts、Reels 内容、发布、快速技巧",
    "Tutorials, business analysis, education, calm summaries": "教程、商业分析、教育、平静总结",
    "Playful tutorials, step lists and checklists, workflows, creator tips, social content": "轻松教程、步骤与清单、工作流程、创作者技巧、社媒内容",
    "Premium personal-brand talks, frameworks and step-by-step methods, product and service intros": "高端个人品牌话题、框架与分步方法、产品与服务介绍",
    "Hooks and high-energy talking-head stretches: launches, pain points, strong claims, one idea per beat": "开场钩子和高能口播段落：发布、痛点、强观点，每拍一个观点",
    "Property tours and listing intros for Reels / TikTok / 小红书 / 抖音": "适用于 Reels、TikTok、小红书、抖音的看房与房源介绍",
    // Pricing page
    "Simple pricing": "简单透明的价格", "Start free. Pay only when you want more.": "免费开始，需要更多时再付费。", "3 free previews": "3 次免费预览",
    "for every new account": "每个新账户", "Credit pack": "点数包", "100 credits": "100 点", "One-time payment · not a subscription": "一次性付款 · 不是订阅",
    "Preview: 12–15 credits": "预览：12–15 点", "HD export (1080p, no watermark): 38–52 credits": "高清导出（1080p，无水印）：38–52 点",
    "You see the exact cost before you start": "开始前会显示确切费用", "Failed renders are refunded automatically": "渲染失败会自动退回",
    "Buy 100 credits": "购买 100 点", "Coming soon: Creator and Pro plans": "即将推出：Creator 和 Pro 套餐",
    "Monthly credits for people who post often. Your current credits and free previews stay as they are.": "为经常发布内容的用户提供每月点数。你现有的点数和免费预览不受影响。",
    "Questions": "常见问题", "Is this a subscription?": "这是订阅吗？",
    "No. $9.99 is a one-time purchase of 100 credits. Buy another pack whenever you need more; nothing renews.": "不是。$9.99 是一次性购买 100 点。需要更多时再买一包即可，不会自动续费。",
    "How are credits used?": "点数怎么使用？",
    "Your first 3 previews are free. After that a preview costs 12–15 credits and a full HD export 38–52, depending on the video's length (up to 30 seconds). The exact cost is shown before you start.": "前 3 次预览免费。之后每次预览 12–15 点，全高清导出 38–52 点，具体取决于视频长度（最长 30 秒）。开始前会显示确切费用。",
    "What do I get with an HD export?": "高清导出包含什么？",
    "The full-length video in 1080p (1080×1920 or 1920×1080), no watermark, rendered from your original upload with the look of the preview you chose. Download it again any time while it's kept.": "完整长度的 1080p 视频（1080×1920 或 1920×1080），无水印，用你的原始视频按所选预览的效果渲染。保存期内可随时再次下载。",
    "What if a render fails?": "渲染失败怎么办？", "It doesn't count: a free preview stays free and credits go straight back to your balance.": "不计次数：免费预览仍然免费，点数直接退回你的余额。",
    "How long are my videos kept?": "视频会保存多久？",
    "Previews and your original upload for 30 days, HD exports for 90 days. Each video shows its expiry date, and you can delete it any time.": "预览和原始视频保存 30 天，高清导出保存 90 天。每个视频都会显示到期日期，你也可以随时删除。",
    "Can I use the music commercially?": "音乐可以商用吗？", "Yes. Every track is an original composition made for EVA Video Studio and is cleared for use in your video.": "可以。每首曲目都是为 EVA Video Studio 创作的原创音乐，已授权用于你的视频。",
    "Refunds": "退款",
    // homepage pricing block
    "Simple credits": "简单的点数制", "No subscription. Your first 3 previews are free. After that a preview costs 12–15 credits and a full 1080p export 38–52, depending on length. You always see the exact cost first.": "无需订阅。前 3 次预览免费。之后每次预览 12–15 点，全 1080p 导出 38–52 点，具体取决于长度。开始前总会显示确切费用。",
    "What if something goes wrong?": "出了问题怎么办？", "If a preview or export can't be rendered, it doesn't count: a free preview stays free and credits go straight back to your balance.": "如果预览或导出无法完成，不会计入：免费预览仍然免费，点数直接退回你的余额。",
    "What happens to my videos?": "我的视频会怎样保存？", "Everything is saved privately in My Videos. Previews and your original upload are kept for 30 days, HD exports for 90 days. Each video shows its expiry date, and you can delete it any time.": "所有内容都私密保存在“我的视频”。预览和原始视频保留 30 天，高清导出保留 90 天。每个视频都会显示到期日期，你也可以随时删除。",
    "The full-length video in 1080p (1080×1920 or 1920×1080), no watermark, rendered from your original upload with the exact look of the preview you chose. Download it again any time while it's kept.": "完整长度的 1080p 视频（1080×1920 或 1920×1080），无水印，用你的原始视频按所选预览的效果渲染。保存期内可随时再次下载。",
    // progress stages
    "Uploaded": "已上传", "Transcribing your voice": "正在识别语音", "Planning captions and cards": "正在规划字幕和卡片", "Rendering video": "正在渲染视频", "Adding music and final checks": "正在添加音乐并做最终检查",
    // API messages (backend stays English; translated here for display)
    "Choose 9:16 or 16:9.": "请选择 9:16 或 16:9。", "Choose at least one visual template.": "请至少选择一个视觉模板。", "Choose one to three music tracks.": "请选择 1 到 3 首曲目。",
    "Choose your settings first.": "请先选择设置。", "The video is larger than 200 MB.": "视频超过 200 MB。", "Upload limit reached for today.": "今天的上传次数已达上限。",
    "Please upload an MP4 (or MOV) video.": "请上传 MP4（或 MOV）视频。", "The upload has not finished yet (or has expired).": "上传尚未完成（或已过期）。",
    "A preview for this video is already being made.": "这个视频的预览正在生成中。", "The original upload for this video has expired, so HD can no longer be rendered.": "这个视频的原始文件已过期，无法再渲染高清版。",
    "This version can't be exported yet.": "这个版本暂时无法导出。", "This video is still rendering.": "这个视频仍在渲染中。", "A version is still rendering.": "仍有版本在渲染中。", "not found": "未找到",
    // page titles
    "EVA Video Studio": "EVA Video Studio", "Template Gallery · EVA Video Studio": "模板库 · EVA Video Studio", "Pricing · EVA Video Studio": "价格 · EVA Video Studio",
    "My Videos · EVA Video Studio": "我的视频 · EVA Video Studio", "My Account · EVA Video Studio": "我的账户 · EVA Video Studio", "Your video · EVA Video Studio": "你的视频 · EVA Video Studio",
  };
  // whole-element translations where the English has inline markup (keyed by the element's English HTML, whitespace collapsed)
  const ZH_HTML = {
    'Your raw clip in. A <span class="grad">finished short</span> out.': '上传原始视频，<br><span class="grad">得到剪好的短视频。</span>',
    '<b>3 free</b> previews': '<b>3 次免费</b>预览', '<b>$9.99</b> = 100 credits': '<b>$9.99</b> = 100 点', 'Ready in about <b>5 minutes</b>': '大约 <b>5 分钟</b>完成',
    '<span aria-hidden="true">＋</span> Make a video': '<span aria-hidden="true">＋</span> 制作视频',
    'Explore all templates <span aria-hidden="true">→</span>': '查看全部模板 <span aria-hidden="true">→</span>',
    'For anything other than a failed render, contact us within 14 days of purchase. See <a href="legal.html">terms, privacy and refunds</a>.': '渲染失败以外的情况，请在购买后 14 天内联系我们。详见<a href="legal.html">条款、隐私与退款</a>。',
  };
  // API messages with numbers (exact text from saas/web/api_v2.py)
  const RX = [
    [/^This video is (\d+) seconds long\. The limit is (\d+) seconds\.$/, "这个视频长 $1 秒，上限为 $2 秒。"],
    [/^This preview costs (\d+) credits and you have (\d+)\. Top up to continue\.$/, "本次预览需 $1 点，你有 $2 点。请充值后继续。"],
    [/^HD export costs (\d+) credits and you have (\d+)\. Top up to continue\.$/, "高清导出需 $1 点，你有 $2 点。请充值后继续。"],
    [/^Request failed \((\d+)\)$/, "请求失败（$1）"],
    [/^This (\d+)-second video fits up to (\d+) templates? \(about (\d+) s each\)\. Choose up to \d+, or upload a longer clip\.$/, "这个 $1 秒的视频最多适合 $2 个模板（每个约 $3 秒）。请少选几个，或上传更长的视频。"],
  ];

  const fill = (s, v) => v ? s.replace(/\{(\w+)\}/g, (m, k) => (v[k] === undefined || v[k] === null) ? "" : String(v[k])) : s;
  function t(s, v) { return fill((lang === "zh" && ZH[s]) || s, v); }
  function msg(s) {   // a message that came from the API or the browser
    if (lang !== "zh" || !s) return s;
    if (ZH[s]) return ZH[s];
    for (const [r, z] of RX) if (r.test(s)) return s.replace(r, z);
    return s;
  }
  const NOT = "script,style,svg,video,audio,[data-no-i18n],textarea,code";
  const ATTRS = ["placeholder", "aria-label", "title", "alt"];
  function trText(n) {
    const p = n.parentElement; if (!p || p.closest(NOT)) return;
    const s = n.nodeValue, k = s.replace(/\s+/g, " ").trim(); if (!k) return;
    const z = ZH[k] || msg(k); if (z && z !== k) n.nodeValue = s.replace(k, z);
  }
  function trAttrs(e) {
    if (e.closest("[data-no-i18n]")) return;
    ATTRS.forEach(a => { const v = e.getAttribute(a); if (v && ZH[v]) e.setAttribute(a, ZH[v]); });
  }
  function apply(root) {
    if (lang !== "zh") return;
    root = root || document.body; if (!root) return;
    if (root.nodeType === 3) return trText(root);
    if (root.nodeType !== 1) return;
    if (root.hasAttribute("data-i18n-html")) { const k = root.innerHTML.replace(/\s+/g, " ").trim(); if (ZH_HTML[k]) root.innerHTML = ZH_HTML[k]; }
    root.querySelectorAll("[data-i18n-html]").forEach(e => { const k = e.innerHTML.replace(/\s+/g, " ").trim(); if (ZH_HTML[k]) e.innerHTML = ZH_HTML[k]; });
    const w = document.createTreeWalker(root, NodeFilter.SHOW_TEXT);
    const nodes = []; while (w.nextNode()) nodes.push(w.currentNode); nodes.forEach(trText);
    trAttrs(root); root.querySelectorAll("[placeholder],[aria-label],[title],img[alt]").forEach(trAttrs);
    if (ZH[document.title]) document.title = ZH[document.title];
  }
  // text that app.js / templates.js add later (status lines, buttons, API labels) is translated as it appears
  function watch() {
    if (lang !== "zh" || !window.MutationObserver) return;
    new MutationObserver(ms => ms.forEach(m => {
      if (m.type === "characterData") trText(m.target);
      else if (m.type === "attributes") { const v = m.target.getAttribute(m.attributeName); if (v && ZH[v] && !m.target.closest("[data-no-i18n]")) m.target.setAttribute(m.attributeName, ZH[v]); }
      else m.addedNodes.forEach(apply);
    })).observe(document.body, { childList: true, subtree: true, characterData: true, attributes: true, attributeFilter: ATTRS });
  }
  function set(l) { try { localStorage.setItem(KEY, l === "zh" ? "zh" : "en"); } catch (e) {}
    const u = new URL(location.href); u.searchParams.delete("lang"); location.replace(u.toString()); }
  // 🌐 EN / 简体中文 switcher in the top-right of the header (before the account avatar)
  function switcher() {
    const nav = document.querySelector(".top nav"); if (!nav || nav.querySelector(".langsw")) return;
    const box = document.createElement("div"); box.className = "langsw";
    box.innerHTML = '<button type="button" class="langbtn" aria-haspopup="menu" aria-expanded="false"><svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="1.8" aria-hidden="true"><circle cx="12" cy="12" r="9"/><path d="M3 12h18M12 3c2.6 2.6 2.6 15.4 0 18M12 3c-2.6 2.6-2.6 15.4 0 18"/></svg><span></span><svg class="car" viewBox="0 0 12 12" width="10" height="10" aria-hidden="true"><path d="M2 4l4 4 4-4" fill="none" stroke="currentColor" stroke-width="1.6"/></svg></button>'
      + '<div class="langmenu" role="menu" hidden><button type="button" role="menuitemradio" data-l="en" lang="en">English</button><button type="button" role="menuitemradio" data-l="zh" lang="zh-CN">简体中文</button></div>';
    const b = box.querySelector(".langbtn"), m = box.querySelector(".langmenu");
    b.querySelector("span").textContent = lang === "zh" ? "中文" : "EN";
    b.setAttribute("aria-label", (lang === "zh" ? "语言：简体中文" : "Language: English"));
    m.querySelectorAll("[data-l]").forEach(x => { x.setAttribute("aria-checked", String(x.dataset.l === lang)); x.onclick = () => x.dataset.l === lang ? close() : set(x.dataset.l); });
    const close = () => { m.hidden = true; b.setAttribute("aria-expanded", "false"); };
    b.onclick = e => { e.stopPropagation(); m.hidden = !m.hidden; b.setAttribute("aria-expanded", String(!m.hidden)); };
    document.addEventListener("click", e => { if (!box.contains(e.target)) close(); });
    document.addEventListener("keydown", e => { if (e.key === "Escape" && !m.hidden) { close(); b.focus(); } });
    const a = nav.querySelector(".acct"); a ? nav.insertBefore(box, a) : nav.append(box);
  }
  document.documentElement.lang = lang === "zh" ? "zh-CN" : "en";
  if (lang === "zh") {   // Chinese fonts: preload the site subset (EVA SC, app.css) and add Google's sliced Noto Sans SC as the last
    const add = (rel, href, extra) => { const l = document.createElement("link"); l.rel = rel; l.href = href; Object.assign(l, extra || {}); document.head.append(l); };
    add("preload", "fonts/eva-sc-400.woff", { as: "font", type: "font/woff", crossOrigin: "anonymous" });   // web fallback for any other character
    add("stylesheet", "https://fonts.googleapis.com/css2?family=Noto+Sans+SC:wght@400;700&display=swap");
  }
  window.I18N = { lang, t, msg, apply, set, locale: lang === "zh" ? "zh-CN" : undefined };
  const boot = () => { switcher(); apply(); watch(); };
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", boot); else boot();
})();
