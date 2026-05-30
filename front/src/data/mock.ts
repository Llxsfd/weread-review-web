export const dashboard = {
  bookCount: 86,
  highlightCount: 1284,
  dueToday: 18,
  overdue: 7,
  reviewedToday: 9,
  latestSync: '2026-05-16 19:42'
}

export const reviewCards = [
  {
    id: 1,
    book: '置身事内',
    author: '兰小欢',
    chapter: '地方政府的权力与事务',
    question: '这条划线如何解释地方政府推动增长的动力？',
    text: '地方政府既是政策执行者，也是地方经济发展的组织者，承担着大量具体而复杂的事务。',
    note: '这里可以和激励机制放在一起看。',
    due: '今天',
    level: 2
  },
  {
    id: 2,
    book: '纳瓦尔宝典',
    author: '埃里克·乔根森',
    chapter: '积累专长',
    question: '为什么专长通常无法通过学校直接获得？',
    text: '专长无法被训练出来，否则人人都能掌握。专长往往来自真正的好奇心和长期积累。',
    note: '',
    due: '逾期 2 天',
    level: 1
  },
  {
    id: 3,
    book: '卡片笔记写作法',
    author: '申克·阿伦斯',
    chapter: '写作不是线性过程',
    question: '这条划线提醒我们如何重新理解写作？',
    text: '写作不是把想法记录下来，而是在记录和连接的过程中产生新的想法。',
    note: '适合放进知识资产的产品介绍里。',
    due: '今天',
    level: 3
  }
]

export const highlights = [
  {
    id: 101,
    book: '置身事内',
    chapter: '地方政府的权力与事务',
    text: '地方政府既是政策执行者，也是地方经济发展的组织者，承担着大量具体而复杂的事务。',
    nextReview: '今天',
    status: '到期'
  },
  {
    id: 102,
    book: '卡片笔记写作法',
    chapter: '写作不是线性过程',
    text: '写作不是把想法记录下来，而是在记录和连接的过程中产生新的想法。',
    nextReview: '2026-05-23',
    status: '进行中'
  },
  {
    id: 103,
    book: '纳瓦尔宝典',
    chapter: '积累专长',
    text: '专长无法被训练出来，否则人人都能掌握。专长往往来自真正的好奇心和长期积累。',
    nextReview: '逾期 2 天',
    status: '困难'
  }
]

export const books = [
  { id: 'b1', title: '置身事内', author: '兰小欢', progress: 100, highlights: 96, due: 6 },
  { id: 'b2', title: '卡片笔记写作法', author: '申克·阿伦斯', progress: 78, highlights: 134, due: 4 },
  { id: 'b3', title: '纳瓦尔宝典', author: '埃里克·乔根森', progress: 100, highlights: 88, due: 8 },
  { id: 'b4', title: '长期主义', author: '高德拉特', progress: 46, highlights: 31, due: 0 }
]

