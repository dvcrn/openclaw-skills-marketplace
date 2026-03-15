#!/bin/bash
# 下载 50 张女性穿搭参考图片
# 来源: Unsplash (CC0 授权)

OUTDIR="/Users/mac/.openclaw/workspace/stylebuddy_v3/assets/images/outfits"
mkdir -p "$OUTDIR"

echo "开始下载 50 张女性穿搭图片..."

# 定义图片关键词和 ID 列表
# 使用 Unsplash Source API 获取图片

# 职场穿搭 (15张)
echo "下载职场穿搭图片..."
curl -sL "https://images.unsplash.com/photo-1594938298603-c8148c4dae35?w=512&h=512&fit=crop" -o "$OUTDIR/work_001.jpg" &
curl -sL "https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?w=512&h=512&fit=crop" -o "$OUTDIR/work_002.jpg" &
curl -sL "https://images.unsplash.com/photo-1581056771107-24ca5f033842?w=512&h=512&fit=crop" -o "$OUTDIR/work_003.jpg" &
curl -sL "https://images.unsplash.com/photo-1574258495973-f010dfbb5371?w=512&h=512&fit=crop" -o "$OUTDIR/work_004.jpg" &
curl -sL "https://images.unsplash.com/photo-1595278069441-2cf29f8005a4?w=512&h=512&fit=crop" -o "$OUTDIR/work_005.jpg" &
curl -sL "https://images.unsplash.com/photo-1551836022-deb4988cc6c0?w=512&h=512&fit=crop" -o "$OUTDIR/work_006.jpg" &
curl -sL "https://images.unsplash.com/photo-1548624149-f321c7e5b42e?w=512&h=512&fit=crop" -o "$OUTDIR/work_007.jpg" &
curl -sL "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=512&h=512&fit=crop" -o "$OUTDIR/work_008.jpg" &
curl -sL "https://images.unsplash.com/photo-1483985988355-763728e1935b?w=512&h=512&fit=crop" -o "$OUTDIR/work_009.jpg" &
curl -sL "https://images.unsplash.com/photo-1551232864-3f522363a84b?w=512&h=512&fit=crop" -o "$OUTDIR/work_010.jpg" &
curl -sL "https://images.unsplash.com/photo-1515886657613-9f3515b0c78f?w=512&h=512&fit=crop" -o "$OUTDIR/work_011.jpg" &
curl -sL "https://images.unsplash.com/photo-1539109136881-3be0616acf4b?w=512&h=512&fit=crop" -o "$OUTDIR/work_012.jpg" &
curl -sL "https://images.unsplash.com/photo-1485968579580-b6d095142e6e?w=512&h=512&fit=crop" -o "$OUTDIR/work_013.jpg" &
curl -sL "https://images.unsplash.com/photo-1496747611176-843222e1e57c?w=512&h=512&fit=crop" -o "$OUTDIR/work_014.jpg" &
curl -sL "https://images.unsplash.com/photo-1485462537746-965f33f7f6a7?w=512&h=512&fit=crop" -o "$OUTDIR/work_015.jpg" &
wait

# 休闲穿搭 (15张)
echo "下载休闲穿搭图片..."
curl -sL "https://images.unsplash.com/photo-1517841905240-472988babdf9?w=512&h=512&fit=crop" -o "$OUTDIR/casual_001.jpg" &
curl -sL "https://images.unsplash.com/photo-1529139574466-a303027c1d8b?w=512&h=512&fit=crop" -o "$OUTDIR/casual_002.jpg" &
curl -sL "https://images.unsplash.com/photo-1502823403499-6ccfcf4fb453?w=512&h=512&fit=crop" -o "$OUTDIR/casual_003.jpg" &
curl -sL "https://images.unsplash.com/photo-1469334031218-e382a71b716b?w=512&h=512&fit=crop" -o "$OUTDIR/casual_004.jpg" &
curl -sL "https://images.unsplash.com/photo-1495385794356-15371f348c31?w=512&h=512&fit=crop" -o "$OUTDIR/casual_005.jpg" &
curl -sL "https://images.unsplash.com/photo-1509631179647-0177331693ae?w=512&h=512&fit=crop" -o "$OUTDIR/casual_006.jpg" &
curl -sL "https://images.unsplash.com/photo-1485962307416-993e145b0d0d?w=512&h=512&fit=crop" -o "$OUTDIR/casual_007.jpg" &
curl -sL "https://images.unsplash.com/photo-1475180429745-b937764fc902?w=512&h=512&fit=crop" -o "$OUTDIR/casual_008.jpg" &
curl -sL "https://images.unsplash.com/photo-1550614000-4b9519e020c9?w=512&h=512&fit=crop" -o "$OUTDIR/casual_009.jpg" &
curl -sL "https://images.unsplash.com/photo-1525507119028-ed4c629a60a3?w=512&h=512&fit=crop" -o "$OUTDIR/casual_010.jpg" &
curl -sL "https://images.unsplash.com/photo-1485230405346-71acb9518d9c?w=512&h=512&fit=crop" -o "$OUTDIR/casual_011.jpg" &
curl -sL "https://images.unsplash.com/photo-1548126032-079a0fb4ce2f?w=512&h=512&fit=crop" -o "$OUTDIR/casual_012.jpg" &
curl -sL "https://images.unsplash.com/photo-1506634572416-48cdfe530110?w=512&h=512&fit=crop" -o "$OUTDIR/casual_013.jpg" &
curl -sL "https://images.unsplash.com/photo-1552374196-1ab2a1c593e8?w=512&h=512&fit=crop" -o "$OUTDIR/casual_014.jpg" &
curl -sL "https://images.unsplash.com/photo-1483985988355-763728e1935b?w=512&h=512&fit=crop" -o "$OUTDIR/casual_015.jpg" &
wait

# 约会穿搭 (10张)
echo "下载约会穿搭图片..."
curl -sL "https://images.unsplash.com/photo-1496747611176-843222e1e57c?w=512&h=512&fit=crop" -o "$OUTDIR/date_001.jpg" &
curl -sL "https://images.unsplash.com/photo-1515372039744-b8f02a3ae446?w=512&h=512&fit=crop" -o "$OUTDIR/date_002.jpg" &
curl -sL "https://images.unsplash.com/photo-1595777457583-95e059d581b8?w=512&h=512&fit=crop" -o "$OUTDIR/date_003.jpg" &
curl -sL "https://images.unsplash.com/photo-1594633312681-425c7b97ccd1?w=512&h=512&fit=crop" -o "$OUTDIR/date_004.jpg" &
curl -sL "https://images.unsplash.com/photo-1566174053879-31528523f8ae?w=512&h=512&fit=crop" -o "$OUTDIR/date_005.jpg" &
curl -sL "https://images.unsplash.com/photo-1550614000-4b9519e020c9?w=512&h=512&fit=crop" -o "$OUTDIR/date_006.jpg" &
curl -sL "https://images.unsplash.com/photo-1545291730-faff8ca1d4b0?w=512&h=512&fit=crop" -o "$OUTDIR/date_007.jpg" &
curl -sL "https://images.unsplash.com/photo-1581044777550-4cfa60707c03?w=512&h=512&fit=crop" -o "$OUTDIR/date_008.jpg" &
curl -sL "https://images.unsplash.com/photo-1496747611176-843222e1e57c?w=512&h=512&fit=crop" -o "$OUTDIR/date_009.jpg" &
curl -sL "https://images.unsplash.com/photo-1564257631407-4deb1f99d992?w=512&h=512&fit=crop" -o "$OUTDIR/date_010.jpg" &
wait

# 运动穿搭 (5张)
echo "下载运动穿搭图片..."
curl -sL "https://images.unsplash.com/photo-1518310383802-640c2de311b2?w=512&h=512&fit=crop" -o "$OUTDIR/sport_001.jpg" &
curl -sL "https://images.unsplash.com/photo-1571902943202-507ec2618e8f?w=512&h=512&fit=crop" -o "$OUTDIR/sport_002.jpg" &
curl -sL "https://images.unsplash.com/photo-1518310952931-b1de897abd40?w=512&h=512&fit=crop" -o "$OUTDIR/sport_003.jpg" &
curl -sL "https://images.unsplash.com/photo-1574680096145-d05b474e2155?w=512&h=512&fit=crop" -o "$OUTDIR/sport_004.jpg" &
curl -sL "https://images.unsplash.com/photo-1541534741688-6078c6bfb5c5?w=512&h=512&fit=crop" -o "$OUTDIR/sport_005.jpg" &
wait

# 其他/聚会/正式穿搭 (5张)
echo "下载其他穿搭图片..."
curl -sL "https://images.unsplash.com/photo-1566174053879-31528523f8ae?w=512&h=512&fit=crop" -o "$OUTDIR/formal_001.jpg" &
curl -sL "https://images.unsplash.com/photo-1595777457583-95e059d581b8?w=512&h=512&fit=crop" -o "$OUTDIR/formal_002.jpg" &
curl -sL "https://images.unsplash.com/photo-1515372039744-b8f02a3ae446?w=512&h=512&fit=crop" -o "$OUTDIR/formal_003.jpg" &
curl -sL "https://images.unsplash.com/photo-1581044777550-4cfa60707c03?w=512&h=512&fit=crop" -o "$OUTDIR/formal_004.jpg" &
curl -sL "https://images.unsplash.com/photo-1545291730-faff8ca1d4b0?w=512&h=512&fit=crop" -o "$OUTDIR/formal_005.jpg" &
wait

echo "图片下载完成！"
echo "下载图片数量: $(ls -1 $OUTDIR/*.jpg 2>/dev/null | wc -l)"
