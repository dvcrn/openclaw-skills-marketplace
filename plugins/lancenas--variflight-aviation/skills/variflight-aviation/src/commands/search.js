const { VariflightClient } = require('../lib/variflight-client');

module.exports = async function search(dep, arr, date) {
    if (!dep || !arr || !date) {
        console.error('Usage: search <dep> <arr> <date>');
        console.error('Example: search PEK SHA 2026-02-20');
        process.exit(1);
    }

    const dateRegex = /^\d{4}-\d{2}-\d{2}$/;
    if (!dateRegex.test(date)) {
        console.error('Error: Date must be in YYYY-MM-DD format');
        process.exit(1);
    }

    if (dep.length !== 3 || arr.length !== 3) {
        console.error('Error: Airport codes must be 3 letters (IATA code)');
        process.exit(1);
    }

    const client = new VariflightClient();

    try {
        console.log(`🔍 搜索 ${dep.toUpperCase()} → ${arr.toUpperCase()} 在 ${date} 的航班...\n`);

        const result = await client.searchFlightsByDepArr(
            dep.toUpperCase(),
            arr.toUpperCase(),
            date
        );

        // 解析标准响应格式 {code, message, data}
        if (!result || result.code !== 200) {
            console.log('❌ 查询失败:', result?.message || '未知错误');
            return;
        }

        const flights = result.data || [];

        if (flights.length === 0) {
            console.log('❌ 未找到航班');
            return;
        }

        console.log(`✈️ 找到 ${flights.length} 个航班：\n`);

        flights.forEach((flight, index) => {
            // 使用实际的字段名（首字母大写）
            const flightNo = flight.FlightNo || '未知航班';
            const airline = flight.FlightCompany || '未知航司';

            // 提取时间（从日期时间字符串中提取时间部分）
            const depDateTime = flight.FlightDeptimePlanDate || '';
            const arrDateTime = flight.FlightArrtimePlanDate || '';
            const depTime = depDateTime.split(' ')[1]?.substring(0, 5) || '待定';
            const arrTime = arrDateTime.split(' ')[1]?.substring(0, 5) || '待定';

            const depAirport = flight.FlightDepcode || dep;
            const arrAirport = flight.FlightArrcode || arr;
            const depTerminal = flight.FlightHTerminal || '';
            const arrTerminal = flight.FlightTerminal || '';

            const aircraft = flight.ftype || flight.generic || '未知机型';
            const status = flight.FlightState || '计划中';

            // 准点率
            const ontimeRate = flight.OntimeRate || '';

            console.log(`${index + 1}. ${flightNo} | ${airline}`);
            console.log(`   🛫 ${depTime} ${depAirport}${depTerminal ? ' T' + depTerminal : ''}`);
            console.log(`   🛬 ${arrTime} ${arrAirport}${arrTerminal ? ' T' + arrTerminal : ''}`);
            console.log(`   ✈️  ${aircraft} | 状态: ${status}${ontimeRate ? ' | 准点率: ' + ontimeRate : ''}`);

            // 额外信息
            if (flight.CheckinTable) {
                console.log(`   🎫 值机柜台: ${flight.CheckinTable}`);
            }
            if (flight.distance) {
                console.log(`   📏 距离: ${flight.distance}公里`);
            }

            console.log('');
        });

    } catch (error) {
        console.error(`❌ 查询失败: ${error.message}`);
        process.exit(1);
    } finally {
        await client.disconnect();
    }
};