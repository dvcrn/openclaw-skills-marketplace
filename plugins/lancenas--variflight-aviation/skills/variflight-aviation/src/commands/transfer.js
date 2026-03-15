const { VariflightClient } = require('../lib/variflight-client');

module.exports = async function transfer(depcity, arrcity, date) {
    if (!depcity || !arrcity || !date) {
        console.error('Usage: transfer <depcity> <arrcity> <date>');
        console.error('Example: transfer BJS SHA 2026-02-20');
        process.exit(1);
    }

    const dateRegex = /^\d{4}-\d{2}-\d{2}$/;
    if (!dateRegex.test(date)) {
        console.error('Error: Date must be in YYYY-MM-DD format');
        process.exit(1);
    }

    const client = new VariflightClient();

    try {
        console.log(`🔄 查询 ${depcity.toUpperCase()} → ${arrcity.toUpperCase()} 在 ${date} 的中转方案...\n`);

        const result = await client.getTransferInfo(
            depcity.toUpperCase(),
            arrcity.toUpperCase(),
            date
        );

        // 解析标准响应格式
        if (!result || result.code !== 200) {
            console.log('❌ 查询失败:', result?.message || '未知错误');
            return;
        }

        const transfers = result.data || [];

        if (transfers.length === 0) {
            console.log('❌ 未找到中转方案');
            return;
        }

        console.log(`找到 ${transfers.length} 个中转方案：\n`);

        transfers.forEach((transfer, index) => {
            const transferCity = transfer.transferCity || transfer.city || '未知中转地';
            const firstFlight = transfer.firstFlight || transfer.flight1 || '未知';
            const secondFlight = transfer.secondFlight || transfer.flight2 || '未知';
            const totalDuration = transfer.totalDuration || transfer.duration || '未知';
            const layover = transfer.layoverDuration || transfer.layover || '未知';
            const price = transfer.price || transfer.minPrice || '未知';

            console.log(`${index + 1}. ${transferCity} 中转`);
            console.log(`   第一程: ${firstFlight}`);
            console.log(`   第二程: ${secondFlight}`);
            console.log(`   总时长: ${totalDuration}分钟`);
            console.log(`   中转时间: ${layover}分钟`);
            console.log(`   价格: ¥${price}`);
            console.log('');
        });

    } catch (error) {
        console.error(`❌ 查询失败: ${error.message}`);
        process.exit(1);
    } finally {
        await client.disconnect();
    }
};