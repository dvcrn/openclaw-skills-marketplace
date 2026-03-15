const { VariflightClient } = require('../lib/variflight-client');

module.exports = async function weather(airport) {
    if (!airport) {
        console.error('Usage: weather <airport>');
        console.error('Example: weather PEK');
        process.exit(1);
    }

    if (airport.length !== 3) {
        console.error('Error: Airport code must be 3 letters (IATA code)');
        process.exit(1);
    }

    const client = new VariflightClient();

    try {
        console.log(`🌤️  查询机场 ${airport.toUpperCase()} 的天气...\n`);

        const result = await client.getAirportWeather(airport.toUpperCase());

        // 解析标准响应格式
        if (!result || result.code !== 200) {
            console.log('❌ 查询失败:', result?.message || '未知错误');
            return;
        }

        const data = result.data || {};

        console.log(`机场: ${airport.toUpperCase()}`);
        console.log('');

        // 天气数据可能是对象或数组
        const weather = Array.isArray(data) ? data[0] : data;

        if (!weather || Object.keys(weather).length === 0) {
            console.log('⚠️  暂无天气数据');
            return;
        }

        // 显示当前天气
        if (weather.current || weather.today) {
            const current = weather.current || weather.today;
            console.log('当前天气:');
            console.log(`  温度: ${current.temp || current.temperature || '未知'}°C`);
            console.log(`  天气: ${current.condition || current.weather || '未知'}`);
            console.log(`  风速: ${current.windSpeed || current.wind || '未知'}`);
            console.log(`  能见度: ${current.visibility || '未知'}km`);
            console.log('');
        }

        // 显示预报
        const forecast = weather.forecast || weather.future || weather.days;
        if (forecast && Array.isArray(forecast)) {
            console.log('未来预报:');
            forecast.slice(0, 3).forEach((day, i) => {
                const date = day.date || day.day || `第${i + 1}天`;
                const condition = day.condition || day.weather || '未知';
                const temp = day.temp || day.temperature ||
                    (day.tempMin && day.tempMax ? `${day.tempMin}°C-${day.tempMax}°C` : '未知');
                console.log(`  ${date}: ${condition}, ${temp}`);
            });
        }

    } catch (error) {
        console.error(`❌ 查询失败: ${error.message}`);
        process.exit(1);
    } finally {
        await client.disconnect();
    }
};