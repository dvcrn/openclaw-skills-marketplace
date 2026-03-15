'use strict';

/**
 * Data Layer
 * Transport: real 12306 data (with mock fallback).
 * Hotels/Attractions: inline mock data (to be replaced by proxy calls).
 *
 * If PLANIT_PROXY_URL is set, all data fetches go through the proxy instead.
 */

const { getTrainOptions } = require('./fetcher/12306');
const { hasStation } = require('./fetcher/stations');
const proxy = require('./fetcher/proxy');

// Approximate distances (km) between cities
const CITY_DISTANCES = {
  '上海-杭州': 180,
  '上海-苏州': 100,
  '上海-南京': 300,
  '上海-黄山': 400,
  '上海-厦门': 900,
  '上海-青岛': 900,
  '上海-北京': 1300,
  '上海-成都': 2000,
  '上海-西安': 1500,
  '上海-广州': 1400,
  '上海-深圳': 1450,
  '上海-丽江': 2500,
  '上海-三亚': 2500,
  '上海-桂林': 1600,
  '上海-武汉': 700,
  '上海-重庆': 1900,
  '上海-张家界': 1200,
  '北京-杭州': 1400,
  '北京-成都': 2000,
  '北京-西安': 1200,
  '北京-广州': 2200,
  '北京-上海': 1300,
};

/**
 * Get approximate distance between two cities.
 */
function getDistance(origin, destination) {
  const key1 = `${origin}-${destination}`;
  const key2 = `${destination}-${origin}`;
  return CITY_DISTANCES[key1] || CITY_DISTANCES[key2] || 800; // default 800km
}

/**
 * Get transport options.
 * Tries 12306 first (real data), falls back to mock if unavailable.
 * @returns {Promise<Array>}
 */
async function getTransportOptions(origin, destination, departureDate, intent, userId) {
  // --- Proxy path (highest priority) ---
  const proxyTrains = await proxy.fetchTrainsViaProxy(origin, destination, departureDate, intent, userId);
  if (proxyTrains) return proxyTrains;

  // --- Direct 12306 path ---
  if (hasStation(origin) && hasStation(destination)) {
    const result = await getTrainOptions(origin, destination, departureDate, 4);
    if (result.trains && result.trains.length > 0) {
      // Annotate with price estimate (12306 doesn't return ticket prices in query)
      const distance = getDistance(origin, destination);
      const annotated = result.trains.map((t) => ({
        ...t,
        price: estimateTrainPrice(t, distance),
        priceUnit: '元/人起',
        note: result.fromCache ? '数据来自缓存' : '数据来自12306',
      }));
      // Append flight option for long routes
      const extras = distance > 800 ? getMockFlightOptions(origin, destination, departureDate, distance) : [];
      return [...annotated, ...extras];
    }
    // 12306 failed or no results — fall through to mock
    console.warn(`[data] 12306 returned no trains for ${origin}→${destination} on ${departureDate}, using mock`);
  }

  // --- Mock fallback ---
  return getMockTransportOptions(origin, destination, departureDate);
}

/**
 * Estimate price based on train type and distance.
 * 12306's query API does not include prices; this is an approximation.
 */
function estimateTrainPrice(train, distance) {
  const rateMap = { high_speed: 0.46, express: 0.30, regular: 0.20 };
  const rate = rateMap[train.subtype] || 0.35;
  return Math.round(distance * rate);
}

/**
 * Mock flight options for long-distance routes.
 */
function getMockFlightOptions(origin, destination, departureDate, distance) {
  return [
    {
      type: 'flight',
      name: '飞机',
      from: `${origin}机场`,
      to: `${destination}机场`,
      departureTime: '09:00',
      arrivalTime: addMinutes('09:00', Math.round(distance / 13) + 60),
      duration: Math.round(distance / 13) + 60,
      price: Math.round(distance * 0.55),
      priceUnit: '元/人起',
      flightNo: `MU${2000 + Math.floor(Math.random() * 8000)}`,
      date: departureDate,
      source: 'mock',
    },
  ];
}

/**
 * Original mock transport (sync, wrapped for fallback).
 */
function getMockTransportOptions(origin, destination, departureDate) {
  const distance = getDistance(origin, destination);
  const options = [];

  if (distance <= 400) {
    // High-speed rail only (short distance)
    options.push({
      type: 'train',
      subtype: 'high_speed',
      name: '高铁',
      from: origin,
      to: destination,
      departureTime: '08:30',
      arrivalTime: addMinutes('08:30', Math.round(distance / 3.0)),
      duration: Math.round(distance / 3.0),
      price: Math.round(distance * 0.45),
      priceUnit: '元/人',
      trainNo: `G${1000 + Math.floor(Math.random() * 9000)}`,
      date: departureDate,
      seatTypes: [
        { type: '二等座', price: Math.round(distance * 0.45) },
        { type: '一等座', price: Math.round(distance * 0.75) },
        { type: '商务座', price: Math.round(distance * 1.5) },
      ],
    });
    options.push({
      type: 'train',
      subtype: 'high_speed',
      name: '高铁（备选）',
      from: origin,
      to: destination,
      departureTime: '14:00',
      arrivalTime: addMinutes('14:00', Math.round(distance / 3.0)),
      duration: Math.round(distance / 3.0),
      price: Math.round(distance * 0.45),
      priceUnit: '元/人',
      trainNo: `G${1000 + Math.floor(Math.random() * 9000)}`,
      date: departureDate,
      seatTypes: [
        { type: '二等座', price: Math.round(distance * 0.45) },
        { type: '一等座', price: Math.round(distance * 0.75) },
      ],
    });
    if (distance <= 200) {
      options.push({
        type: 'bus',
        name: '大巴',
        from: origin,
        to: destination,
        departureTime: '09:00',
        arrivalTime: addMinutes('09:00', Math.round(distance / 1.2)),
        duration: Math.round(distance / 1.2),
        price: Math.round(distance * 0.15),
        priceUnit: '元/人',
        date: departureDate,
      });
    }
  } else if (distance <= 1000) {
    // High-speed rail + optional flight
    options.push({
      type: 'train',
      subtype: 'high_speed',
      name: '高铁',
      from: origin,
      to: destination,
      departureTime: '07:00',
      arrivalTime: addMinutes('07:00', Math.round(distance / 2.5)),
      duration: Math.round(distance / 2.5),
      price: Math.round(distance * 0.5),
      priceUnit: '元/人',
      trainNo: `G${1000 + Math.floor(Math.random() * 9000)}`,
      date: departureDate,
      seatTypes: [
        { type: '二等座', price: Math.round(distance * 0.5) },
        { type: '一等座', price: Math.round(distance * 0.85) },
      ],
    });
    options.push({
      type: 'flight',
      name: '飞机',
      from: `${origin}浦东` ,
      to: `${destination}机场`,
      departureTime: '09:30',
      arrivalTime: addMinutes('09:30', Math.round(distance / 12) + 60),
      duration: Math.round(distance / 12) + 60,
      price: Math.round(distance * 0.6),
      priceUnit: '元/人起',
      flightNo: `MU${2000 + Math.floor(Math.random() * 8000)}`,
      date: departureDate,
    });
  } else {
    // Long distance: flight preferred
    options.push({
      type: 'flight',
      name: '飞机（推荐）',
      from: `${origin}浦东`,
      to: `${destination}机场`,
      departureTime: '08:00',
      arrivalTime: addMinutes('08:00', Math.round(distance / 14) + 60),
      duration: Math.round(distance / 14) + 60,
      price: Math.round(distance * 0.55),
      priceUnit: '元/人起',
      flightNo: `CA${3000 + Math.floor(Math.random() * 7000)}`,
      date: departureDate,
    });
    options.push({
      type: 'flight',
      name: '飞机（备选）',
      from: `${origin}浦东`,
      to: `${destination}机场`,
      departureTime: '13:00',
      arrivalTime: addMinutes('13:00', Math.round(distance / 14) + 60),
      duration: Math.round(distance / 14) + 60,
      price: Math.round(distance * 0.65),
      priceUnit: '元/人起',
      flightNo: `MU${2000 + Math.floor(Math.random() * 8000)}`,
      date: departureDate,
    });
    if (distance <= 2000) {
      options.push({
        type: 'train',
        subtype: 'high_speed',
        name: '高铁',
        from: origin,
        to: destination,
        departureTime: '06:30',
        arrivalTime: addMinutes('06:30', Math.round(distance / 2.2)),
        duration: Math.round(distance / 2.2),
        price: Math.round(distance * 0.55),
        priceUnit: '元/人',
        trainNo: `G${1000 + Math.floor(Math.random() * 9000)}`,
        date: departureDate,
        seatTypes: [
          { type: '二等座', price: Math.round(distance * 0.55) },
          { type: '一等座', price: Math.round(distance * 0.9) },
        ],
      });
    }
  }

  return options;
}

/**
 * Add minutes to a HH:MM time string. Handles crossing midnight.
 */
function addMinutes(timeStr, minutes) {
  const [h, m] = timeStr.split(':').map(Number);
  const total = h * 60 + m + minutes;
  const newH = Math.floor(total / 60) % 24;
  const newM = total % 60;
  return `${String(newH).padStart(2, '0')}:${String(newM).padStart(2, '0')}`;
}

// Hotels database by city
const HOTELS_DB = {
  '杭州': [
    {
      id: 'hz_001',
      name: '西湖国宾馆',
      stars: 5,
      location: '西湖景区',
      address: '杭州市西湖区北山街1号',
      tags: ['景区内', '历史建筑', '适合老人'],
      pricePerNight: 1800,
      rating: 4.9,
      features: ['湖景房', '无障碍设施', '中餐厅', '免费停车'],
      imageUrl: null,
    },
    {
      id: 'hz_002',
      name: '杭州滨江希尔顿酒店',
      stars: 5,
      location: '钱塘江边',
      address: '杭州市滨江区滨盛路1711号',
      tags: ['高端商务', '江景'],
      pricePerNight: 980,
      rating: 4.8,
      features: ['江景房', '健身房', '游泳池', '全日餐厅'],
      imageUrl: null,
    },
    {
      id: 'hz_003',
      name: '杭州西溪悦榕庄',
      stars: 5,
      location: '西溪湿地',
      address: '杭州市余杭区天目山路800号',
      tags: ['度假', '生态', '情侣'],
      pricePerNight: 2200,
      rating: 4.9,
      features: ['私人庭院', 'SPA', '观鸟', '自然风光'],
      imageUrl: null,
    },
    {
      id: 'hz_004',
      name: '如家酒店（杭州西湖店）',
      stars: 2,
      location: '西湖附近',
      address: '杭州市上城区南山路288号',
      tags: ['经济', '交通便利'],
      pricePerNight: 280,
      rating: 4.3,
      features: ['地铁口', '早餐', '24小时前台'],
      imageUrl: null,
    },
    {
      id: 'hz_005',
      name: '杭州花间堂·西湖',
      stars: 4,
      location: '西湖边',
      address: '杭州市上城区湖滨路7号',
      tags: ['精品', '中式', '湖景'],
      pricePerNight: 680,
      rating: 4.7,
      features: ['湖景阳台', '中式庭院', '茶室', '景区步行'],
      imageUrl: null,
    },
  ],
  '上海': [
    {
      id: 'sh_001',
      name: '上海和平饭店',
      stars: 5,
      location: '外滩',
      address: '上海市黄浦区南京东路20号',
      tags: ['历史', '外滩', '标志性'],
      pricePerNight: 2500,
      rating: 4.9,
      features: ['外滩江景', 'Jazz Bar', '历史建筑', '顶层餐厅'],
      imageUrl: null,
    },
    {
      id: 'sh_002',
      name: '上海中心J酒店',
      stars: 5,
      location: '陆家嘴',
      address: '上海市浦东新区银城中路501号',
      tags: ['超高层', '奢华', '陆家嘴'],
      pricePerNight: 3200,
      rating: 4.9,
      features: ['百层以上客房', '城市全景', '米其林餐厅', '无边泳池'],
      imageUrl: null,
    },
    {
      id: 'sh_003',
      name: '汉庭酒店（上海人民广场店）',
      stars: 2,
      location: '人民广场',
      address: '上海市黄浦区西藏中路88号',
      tags: ['经济', '地铁'],
      pricePerNight: 260,
      rating: 4.2,
      features: ['人民广场地铁站', '早餐', '中心地段'],
      imageUrl: null,
    },
    {
      id: 'sh_004',
      name: '朱家角安麓',
      stars: 5,
      location: '朱家角古镇',
      address: '上海市青浦区朱家角镇漕平路2000号',
      tags: ['古镇', '度假', '江南'],
      pricePerNight: 2800,
      rating: 4.9,
      features: ['明清建筑', '私家码头', 'SPA', '古镇内'],
      imageUrl: null,
    },
    {
      id: 'sh_005',
      name: '上海虹桥雅高美爵酒店',
      stars: 4,
      location: '虹桥',
      address: '上海市长宁区虹桥路1700号',
      tags: ['商务', '交通枢纽'],
      pricePerNight: 650,
      rating: 4.5,
      features: ['高铁站步行', '商务设施', '健身房', '全日餐厅'],
      imageUrl: null,
    },
  ],
  '北京': [
    {
      id: 'bj_001',
      name: '北京王府井希尔顿',
      stars: 5,
      location: '王府井',
      address: '北京市东城区王府井大街1号',
      tags: ['市中心', '购物', '老人友好'],
      pricePerNight: 1200,
      rating: 4.8,
      features: ['王府井步行街', '中餐厅', '健身房', '无障碍'],
      imageUrl: null,
    },
    {
      id: 'bj_002',
      name: '北京颐和安缦',
      stars: 5,
      location: '颐和园',
      address: '北京市海淀区公主坟颐和园宫门倒座房1-12号',
      tags: ['奢华', '皇家园林', '历史'],
      pricePerNight: 8000,
      rating: 5.0,
      features: ['园林内住宿', '私人管家', '古建筑', '园景'],
      imageUrl: null,
    },
    {
      id: 'bj_003',
      name: '如家酒店（北京天安门广场店）',
      stars: 2,
      location: '天安门',
      address: '北京市东城区前门大街1号',
      tags: ['经济', '景区近'],
      pricePerNight: 320,
      rating: 4.3,
      features: ['步行天安门', '地铁站', '早餐'],
      imageUrl: null,
    },
    {
      id: 'bj_004',
      name: '北京木棉花酒店',
      stars: 5,
      location: '西城区',
      address: '北京市西城区金融大街10号',
      tags: ['商务', '金融街'],
      pricePerNight: 1500,
      rating: 4.7,
      features: ['金融街', '会议设施', '行政酒廊', '健身中心'],
      imageUrl: null,
    },
    {
      id: 'bj_005',
      name: '北京家庭客栈（胡同院落）',
      stars: 3,
      location: '南锣鼓巷',
      address: '北京市东城区南锣鼓巷附近',
      tags: ['文艺', '胡同', '体验'],
      pricePerNight: 480,
      rating: 4.6,
      features: ['四合院', '胡同体验', '文艺氛围', '自行车租借'],
      imageUrl: null,
    },
  ],
  '成都': [
    {
      id: 'cd_001',
      name: '成都博舍',
      stars: 5,
      location: '太古里',
      address: '成都市锦江区中纱帽街9号',
      tags: ['市中心', '文化', '精品'],
      pricePerNight: 1600,
      rating: 4.9,
      features: ['大慈寺旁', '文化体验', '精品餐厅', '地道川菜'],
      imageUrl: null,
    },
    {
      id: 'cd_002',
      name: '成都瑞吉酒店',
      stars: 5,
      location: '天府广场',
      address: '成都市青羊区东城根上街199号',
      tags: ['奢华', '市中心'],
      pricePerNight: 1200,
      rating: 4.8,
      features: ['管家服务', '私人调酒', 'SPA', '全景城市'],
      imageUrl: null,
    },
    {
      id: 'cd_003',
      name: '维也纳酒店（成都宽窄巷子店）',
      stars: 3,
      location: '宽窄巷子',
      address: '成都市青羊区宽巷子38号',
      tags: ['中等', '景区'],
      pricePerNight: 380,
      rating: 4.4,
      features: ['步行宽窄巷子', '早餐', '中式装修'],
      imageUrl: null,
    },
    {
      id: 'cd_004',
      name: '汉庭酒店（成都春熙路店）',
      stars: 2,
      location: '春熙路',
      address: '成都市锦江区春熙路99号',
      tags: ['经济', '购物'],
      pricePerNight: 220,
      rating: 4.2,
      features: ['春熙路商圈', '地铁站', '早餐'],
      imageUrl: null,
    },
    {
      id: 'cd_005',
      name: '青城山六善酒店',
      stars: 5,
      location: '青城山',
      address: '成都市都江堰市青城山镇青城山路1号',
      tags: ['度假', '山景', '禅意'],
      pricePerNight: 2400,
      rating: 4.9,
      features: ['山间溪流', 'SPA', '有机餐厅', '冥想课程'],
      imageUrl: null,
    },
  ],
  '三亚': [
    {
      id: 'sy_001',
      name: '三亚亚龙湾万豪度假酒店',
      stars: 5,
      location: '亚龙湾',
      address: '三亚市亚龙湾国家旅游度假区',
      tags: ['海滩', '度假', '奢华'],
      pricePerNight: 2000,
      rating: 4.8,
      features: ['私家海滩', '多个泳池', '水上运动', '儿童乐园'],
      imageUrl: null,
    },
    {
      id: 'sy_002',
      name: '三亚海棠湾万象悦来',
      stars: 5,
      location: '海棠湾',
      address: '三亚市海棠区海棠湾路1号',
      tags: ['免税区', '家庭', '度假'],
      pricePerNight: 1600,
      rating: 4.7,
      features: ['免税购物', '亲子设施', '海景', '多个餐厅'],
      imageUrl: null,
    },
    {
      id: 'sy_003',
      name: '三亚半山半岛安纳塔拉',
      stars: 5,
      location: '鹿回头',
      address: '三亚市河西区南边海路2号',
      tags: ['奢华', '山海', '情侣'],
      pricePerNight: 3500,
      rating: 4.9,
      features: ['无边泳池', 'SPA', '私人沙滩', '崖顶别墅'],
      imageUrl: null,
    },
    {
      id: 'sy_004',
      name: '如家酒店（三亚大东海店）',
      stars: 2,
      location: '大东海',
      address: '三亚市吉阳区大东海旅游区',
      tags: ['经济', '海边'],
      pricePerNight: 320,
      rating: 4.1,
      features: ['步行海滩', '早餐', '免费停车'],
      imageUrl: null,
    },
    {
      id: 'sy_005',
      name: '三亚太阳湾柏悦酒店',
      stars: 5,
      location: '太阳湾',
      address: '三亚市吉阳区太阳湾路1号',
      tags: ['隐秘', '高端', '度假'],
      pricePerNight: 4200,
      rating: 5.0,
      features: ['私密海湾', '直升机坪', 'SPA', '米其林餐厅'],
      imageUrl: null,
    },
  ],
  '西安': [
    {
      id: 'xa_001',
      name: '西安钟楼万达文华酒店',
      stars: 5,
      location: '钟鼓楼',
      address: '西安市碑林区南大街88号',
      tags: ['市中心', '景区', '老人友好'],
      pricePerNight: 900,
      rating: 4.8,
      features: ['步行钟楼', '中餐厅', '无障碍设施', '出租车便利'],
      imageUrl: null,
    },
    {
      id: 'xa_002',
      name: '西安曲江悦椿温泉酒店',
      stars: 5,
      location: '曲江',
      address: '西安市雁塔区曲江新区芙蓉西路99号',
      tags: ['温泉', '度假', '文化'],
      pricePerNight: 1200,
      rating: 4.8,
      features: ['室内温泉', '曲江景区', '唐文化', '健身SPA'],
      imageUrl: null,
    },
    {
      id: 'xa_003',
      name: '汉庭酒店（西安回民街店）',
      stars: 2,
      location: '回民街',
      address: '西安市莲湖区北院门附近',
      tags: ['经济', '美食街'],
      pricePerNight: 200,
      rating: 4.3,
      features: ['步行回民街', '清真早餐', '城墙附近'],
      imageUrl: null,
    },
    {
      id: 'xa_004',
      name: '西安皇城相府精品酒店',
      stars: 4,
      location: '顺城巷',
      address: '西安市碑林区顺城巷东段',
      tags: ['精品', '城墙脚下', '文化'],
      pricePerNight: 560,
      rating: 4.6,
      features: ['城墙骑行入口', '陕菜餐厅', '历史文化', '庭院'],
      imageUrl: null,
    },
    {
      id: 'xa_005',
      name: '西安临潼华清城艾美酒店',
      stars: 5,
      location: '骊山脚下',
      address: '西安市临潼区华清池路38号',
      tags: ['景区内', '华清池', '历史'],
      pricePerNight: 1500,
      rating: 4.7,
      features: ['华清池内', '温泉', '骊山缆车', '演出观看'],
      imageUrl: null,
    },
  ],
  '丽江': [
    {
      id: 'lj_001',
      name: '丽江悦榕庄',
      stars: 5,
      location: '拉市海',
      address: '丽江市古城区拉市海风景区',
      tags: ['奢华', '度假', '情侣'],
      pricePerNight: 3800,
      rating: 4.9,
      features: ['湖景别墅', '马术', 'SPA', '私人管家'],
      imageUrl: null,
    },
    {
      id: 'lj_002',
      name: '丽江古城花间堂',
      stars: 4,
      location: '古城内',
      address: '丽江市古城区五一街酒吧街',
      tags: ['精品', '古城', '文艺'],
      pricePerNight: 780,
      rating: 4.7,
      features: ['古城核心', '纳西文化', '烤火庭院', '雪山景观'],
      imageUrl: null,
    },
    {
      id: 'lj_003',
      name: '丽江束河院子精品酒店',
      stars: 3,
      location: '束河古镇',
      address: '丽江市古城区束河镇兴文路',
      tags: ['中等', '古镇', '安静'],
      pricePerNight: 420,
      rating: 4.5,
      features: ['束河古镇内', '玉龙雪山景', '烤火', '纳西早餐'],
      imageUrl: null,
    },
    {
      id: 'lj_004',
      name: '汉庭酒店（丽江古城店）',
      stars: 2,
      location: '古城附近',
      address: '丽江市古城区福慧路9号',
      tags: ['经济', '交通便利'],
      pricePerNight: 180,
      rating: 4.1,
      features: ['步行古城', '停车场', '早餐'],
      imageUrl: null,
    },
    {
      id: 'lj_005',
      name: '玉龙雪山国际大酒店',
      stars: 4,
      location: '玉龙雪山景区',
      address: '丽江市古城区玉龙雪山景区内',
      tags: ['景区', '雪山', '独特'],
      pricePerNight: 980,
      rating: 4.6,
      features: ['雪山脚下', '高原体验', '藏式餐厅', '索道便利'],
      imageUrl: null,
    },
  ],
};

// Default hotel set for cities not in DB
const DEFAULT_HOTELS = (city) => [
  {
    id: `${city}_001`,
    name: `${city}万豪酒店`,
    stars: 5,
    location: '市中心',
    address: `${city}市中心区`,
    tags: ['高端', '市中心'],
    pricePerNight: 1200,
    rating: 4.8,
    features: ['市中心位置', '健身房', '餐厅', '商务设施'],
    imageUrl: null,
  },
  {
    id: `${city}_002`,
    name: `${city}精选酒店`,
    stars: 4,
    location: '景区附近',
    address: `${city}市景区路1号`,
    tags: ['中高端', '景区近'],
    pricePerNight: 650,
    rating: 4.6,
    features: ['景区附近', '舒适客房', '早餐', '接送服务'],
    imageUrl: null,
  },
  {
    id: `${city}_003`,
    name: `${city}文旅民宿`,
    stars: 3,
    location: '古城区',
    address: `${city}市文化街区`,
    tags: ['精品', '文化', '体验'],
    pricePerNight: 380,
    rating: 4.5,
    features: ['本地特色', '文化体验', '温馨服务', '家常早餐'],
    imageUrl: null,
  },
  {
    id: `${city}_004`,
    name: `如家酒店（${city}店）`,
    stars: 2,
    location: '交通枢纽',
    address: `${city}市火车站附近`,
    tags: ['经济', '交通便利'],
    pricePerNight: 220,
    rating: 4.2,
    features: ['火车站附近', '早餐', '24h前台', '停车'],
    imageUrl: null,
  },
  {
    id: `${city}_005`,
    name: `${city}商务快捷酒店`,
    stars: 2,
    location: '商业区',
    address: `${city}市商业中心`,
    tags: ['经济', '商务'],
    pricePerNight: 180,
    rating: 4.0,
    features: ['商业区', 'Wi-Fi', '早餐可选', '停车场'],
    imageUrl: null,
  },
];

/**
 * Get hotels for a city — proxy first, mock fallback.
 */
async function getHotels(city, userId = 'anonymous') {
  const proxyHotels = await proxy.fetchHotelsViaProxy(city, userId);
  if (proxyHotels) return proxyHotels;
  return HOTELS_DB[city] || DEFAULT_HOTELS(city);
}

// Attractions database by city
const ATTRACTIONS_DB = {
  '杭州': [
    { id: 'hz_a1', name: '西湖风景区', category: '自然/文化', duration: 180, price: 0, tags: ['湖泊', '历史', '步行'], suitable: ['elderly', 'family', 'couple', 'general'], tips: '建议上午游览，避开人流高峰' },
    { id: 'hz_a2', name: '灵隐寺', category: '宗教/文化', duration: 120, price: 45, tags: ['寺庙', '历史', '爬山'], suitable: ['general', 'family', 'elderly'], tips: '建议早晨前往，氛围更好' },
    { id: 'hz_a3', name: '宋城景区', category: '主题公园', duration: 180, price: 280, tags: ['演出', '主题园', '适合家庭'], suitable: ['family', 'family_kids', 'general'], tips: '《宋城千古情》演出是必看节目' },
    { id: 'hz_a4', name: '河坊街历史街区', category: '美食/购物', duration: 90, price: 0, tags: ['小吃', '古街', '购物'], suitable: ['elderly', 'general', 'friends'], tips: '西湖醋鱼、龙井虾仁必尝' },
    { id: 'hz_a5', name: '西溪国家湿地公园', category: '自然', duration: 150, price: 80, tags: ['湿地', '鸟类', '划船'], suitable: ['family', 'elderly', 'couple'], tips: '乘船游览最佳，适合老人' },
    { id: 'hz_a6', name: '雷峰塔', category: '历史/文化', duration: 60, price: 40, tags: ['塔', '白蛇传', '西湖'], suitable: ['general', 'elderly', 'couple'], tips: '登顶可俯瞰整个西湖' },
    { id: 'hz_a7', name: '龙井茶园', category: '文化体验', duration: 90, price: 0, tags: ['茶园', '采茶', '体验'], suitable: ['elderly', 'general', 'couple'], tips: '可品茶、采茶，适合慢游' },
  ],
  '北京': [
    { id: 'bj_a1', name: '故宫博物院', category: '历史/文化', duration: 240, price: 60, tags: ['皇宫', '历史', '博物馆'], suitable: ['general', 'elderly', 'family'], tips: '提前网上预约，建议全天游览' },
    { id: 'bj_a2', name: '长城（八达岭）', category: '历史/自然', duration: 300, price: 40, tags: ['长城', '爬山', '历史'], suitable: ['general', 'friends'], tips: '老人建议选徒步少的段落，共乘缆车' },
    { id: 'bj_a3', name: '天坛公园', category: '历史/文化', duration: 120, price: 15, tags: ['皇家祭坛', '园林', '太极'], suitable: ['elderly', 'general'], tips: '早晨有晨练的北京市民，氛围极好' },
    { id: 'bj_a4', name: '颐和园', category: '皇家园林', duration: 180, price: 30, tags: ['园林', '湖泊', '历史'], suitable: ['elderly', 'general', 'couple'], tips: '乘船游览昆明湖，景色宜人，老人友好' },
    { id: 'bj_a5', name: '南锣鼓巷', category: '美食/文化', duration: 90, price: 0, tags: ['胡同', '美食', '文艺'], suitable: ['friends', 'couple', 'general'], tips: '下午3点后人少，炸酱面必吃' },
    { id: 'bj_a6', name: '国家博物馆', category: '博物馆', duration: 180, price: 0, tags: ['历史', '文物', '免费'], suitable: ['general', 'elderly', 'family'], tips: '免费但需预约，文物珍贵值得细看' },
  ],
  '成都': [
    { id: 'cd_a1', name: '大熊猫繁育研究基地', category: '自然/科普', duration: 180, price: 55, tags: ['熊猫', '自然', '科普'], suitable: ['family_kids', 'general', 'elderly'], tips: '上午8-10点熊猫最活跃，建议早去' },
    { id: 'cd_a2', name: '宽窄巷子', category: '历史/美食', duration: 120, price: 0, tags: ['古巷', '美食', '文化'], suitable: ['general', 'elderly', 'friends'], tips: '兔头、钵钵鸡、三大炮必尝' },
    { id: 'cd_a3', name: '锦里古街', category: '历史/美食', duration: 90, price: 0, tags: ['古街', '小吃', '购物'], suitable: ['general', 'family', 'elderly'], tips: '紧邻武侯祠，可一并游览' },
    { id: 'cd_a4', name: '青城山', category: '道教/自然', duration: 300, price: 90, tags: ['道教', '爬山', '自然'], suitable: ['general', 'friends'], tips: '前山适合游览，后山适合徒步' },
    { id: 'cd_a5', name: '都江堰景区', category: '世界遗产', duration: 240, price: 80, tags: ['水利工程', '世界遗产', '历史'], suitable: ['general', 'elderly', 'family'], tips: '与青城山相邻，可联票游览' },
    { id: 'cd_a6', name: '武侯祠博物馆', category: '历史/文化', duration: 120, price: 50, tags: ['三国', '历史', '博物馆'], suitable: ['general', 'elderly'], tips: '三国文化爱好者必去' },
  ],
  '三亚': [
    { id: 'sy_a1', name: '亚龙湾热带天堂森林公园', category: '自然', duration: 180, price: 75, tags: ['热带雨林', '索道', '自然'], suitable: ['general', 'family', 'friends'], tips: '乘坐索道俯瞰海湾，景色绝美' },
    { id: 'sy_a2', name: '天涯海角', category: '自然/文化', duration: 90, price: 81, tags: ['海岸', '礁石', '爱情'], suitable: ['couple', 'general', 'elderly'], tips: '象征忠贞爱情，情侣必去' },
    { id: 'sy_a3', name: '南山文化旅游区', category: '佛教/文化', duration: 180, price: 145, tags: ['南海观音', '佛教', '文化'], suitable: ['elderly', 'general', 'family'], tips: '老人祈福圣地，适合全家' },
    { id: 'sy_a4', name: '蜈支洲岛', category: '海洋/运动', duration: 300, price: 198, tags: ['潜水', '海岛', '水上运动'], suitable: ['friends', 'couple', 'general'], tips: '潜水看珊瑚，夏威夷风情' },
    { id: 'sy_a5', name: '大东海', category: '海滩', duration: 120, price: 0, tags: ['海滩', '免费', '游泳'], suitable: ['general', 'family_kids', 'friends'], tips: '免费海滩，设施完善，水质清澈' },
  ],
  '西安': [
    { id: 'xa_a1', name: '秦始皇兵马俑博物馆', category: '世界遗产', duration: 240, price: 120, tags: ['世界奇迹', '历史', '博物馆'], suitable: ['general', 'elderly', 'family'], tips: '建议请讲解员，历史背景丰富' },
    { id: 'xa_a2', name: '大雁塔·大唐芙蓉园', category: '历史/文化', duration: 180, price: 120, tags: ['唐文化', '大雁塔', '夜游'], suitable: ['general', 'couple', 'elderly'], tips: '夜游大唐芙蓉园别有风情' },
    { id: 'xa_a3', name: '回民街', category: '美食', duration: 120, price: 0, tags: ['美食街', '清真', '小吃'], suitable: ['general', 'elderly', 'friends'], tips: '肉夹馍、羊肉泡馍必吃，老人慢逛舒适' },
    { id: 'xa_a4', name: '西安城墙', category: '历史/文化', duration: 90, price: 54, tags: ['古城墙', '骑行', '历史'], suitable: ['general', 'friends', 'couple'], tips: '租自行车骑行城墙一圈，约13.7公里' },
    { id: 'xa_a5', name: '华清宫·骊山', category: '历史/温泉', duration: 180, price: 120, tags: ['温泉', '历史', '杨贵妃'], suitable: ['elderly', 'couple', 'general'], tips: '《长恨歌》大型实景演出值得观看' },
  ],
  '丽江': [
    { id: 'lj_a1', name: '丽江古城', category: '历史/文化', duration: 180, price: 0, tags: ['古城', '纳西族', '世界遗产'], suitable: ['general', 'elderly', 'couple'], tips: '傍晚漫步酒吧街，氛围最佳' },
    { id: 'lj_a2', name: '玉龙雪山', category: '自然', duration: 300, price: 230, tags: ['雪山', '高原', '索道'], suitable: ['general', 'friends', 'couple'], tips: '高原缺氧，老人和心脏病患者需谨慎' },
    { id: 'lj_a3', name: '束河古镇', category: '历史/文化', duration: 120, price: 0, tags: ['古镇', '安静', '纳西'], suitable: ['general', 'elderly', 'couple'], tips: '比古城安静，保留更多纳西族风情' },
    { id: 'lj_a4', name: '泸沽湖', category: '自然/民族', duration: 360, price: 100, tags: ['湖泊', '摩梭族', '骑行'], suitable: ['friends', 'couple', 'general'], tips: '摩梭族走婚文化独特，湖色纯净' },
    { id: 'lj_a5', name: '白沙壁画', category: '历史/艺术', duration: 60, price: 15, tags: ['壁画', '古代艺术', '纳西'], suitable: ['general', 'elderly'], tips: '珍贵的纳西族历史文化遗存' },
  ],
};

const DEFAULT_ATTRACTIONS = (city) => [
  { id: `${city}_a1`, name: `${city}主要景区`, category: '自然/文化', duration: 180, price: 50, tags: ['景区', '游览'], suitable: ['general', 'elderly', 'family', 'friends', 'couple'], tips: '建议上午游览' },
  { id: `${city}_a2`, name: `${city}历史博物馆`, category: '历史/文化', duration: 120, price: 20, tags: ['博物馆', '历史', '文化'], suitable: ['general', 'elderly', 'family'], tips: '了解当地历史文化' },
  { id: `${city}_a3`, name: `${city}美食街`, category: '美食', duration: 90, price: 0, tags: ['美食', '小吃', '购物'], suitable: ['general', 'elderly', 'friends'], tips: '品尝当地特色美食' },
  { id: `${city}_a4`, name: `${city}自然公园`, category: '自然', duration: 150, price: 30, tags: ['公园', '散步', '自然'], suitable: ['elderly', 'family', 'couple', 'general'], tips: '适合悠闲游览' },
];

/**
 * Get attractions for a city — proxy first, mock fallback.
 */
async function getAttractions(city, group = 'general', userId = 'anonymous') {
  const proxyAttractions = await proxy.fetchAttractionsViaProxy(city, group, userId);
  if (proxyAttractions) return proxyAttractions;

  const all = ATTRACTIONS_DB[city] || DEFAULT_ATTRACTIONS(city);
  return all.sort((a, b) => {
    const aOk = a.suitable.includes(group) || a.suitable.includes('general') ? 0 : 1;
    const bOk = b.suitable.includes(group) || b.suitable.includes('general') ? 0 : 1;
    return aOk - bOk;
  });
}

module.exports = { getTransportOptions, getHotels, getAttractions, getDistance };
