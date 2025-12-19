// 测试多图模式解析函数

function parseMultiGenerationPrompt(prompt) {
    // 解析多图生成提示词
    const patterns = [
        // "生成3张xxx" 或 "画5个yyy"
        { regex: /^(?:生成|画|创作|做)?\s*(\d+|[一二三四五六七八九十]+)\s*(?:张|个|幅)\s*(.+)$/i, countIndex: 1, descIndex: 2 },
        // "xxx 3张" 或 "yyy 5个"
        { regex: /^(.+?)\s+(\d+|[一二三四五六七八九十]+)\s*(?:张|个|幅)$/i, countIndex: 2, descIndex: 1 },
        // "3张 xxx"
        { regex: /^(\d+|[一二三四五六七八九十]+)\s*(?:张|个|幅)\s+(.+)$/i, countIndex: 1, descIndex: 2 }
    ];
    
    // 中文数字转换
    const chineseNums = {
        '一': 1, '二': 2, '三': 3, '四': 4, '五': 5,
        '六': 6, '七': 7, '八': 8, '九': 9, '十': 10
    };
    
    for (const pattern of patterns) {
        const match = prompt.match(pattern.regex);
        if (match) {
            let countStr = match[pattern.countIndex];
            const description = match[pattern.descIndex].trim();
            
            // 转换数量
            let count = chineseNums[countStr] || parseInt(countStr);
            
            if (count && description) {
                return { count, description };
            }
        }
    }
    
    // 如果没有匹配到明确的格式，返回0
    return { count: 0, description: prompt };
}

// 测试用例
const testCases = [
    "3张 熊猫",
    "生成5个风景",
    "画二张中国风建筑",
    "风景画 4个",
    "可爱的小猫 3张",
    "生成一些图片",  // 应该失败
    "很多张猫",      // 应该失败
];

console.log("🧪 测试多图模式解析\n");

testCases.forEach(test => {
    const result = parseMultiGenerationPrompt(test);
    if (result.count > 0) {
        console.log(`✅ "${test}"`);
        console.log(`   数量: ${result.count}, 描述: "${result.description}"\n`);
    } else {
        console.log(`❌ "${test}"`);
        console.log(`   解析失败\n`);
    }
});
