> 收集整理一周所见所闻，包含技术文章资料，开源项目和一些网站工具
> 
> 时间：20240819-20240825
> 
> 周数：第34周



## 📜有价值的文章

#### [tacit knowledge dangerous](https://er4hn.info/blog/2023.08.26-tacit-knowledge-dangerous/)

文章介绍了团队开发内部存在的隐形知识问题，也就是那些没有文档化大家口口相传的一些约定和配置信息，但是伴随着项目的复杂化和团队成员的增加，这种看起来很方便的方式会产生巨大的问题。

1. 首先便是这类知识的掌握者不得不一遍又一遍的给别人讲解造成时间的浪费，和正在工作内容的延后；
2. 其次知识的持有者并不是每时每刻都能回复你的疑问，如果是跨时区的协作工作就更加困难；
3. 最后虽然查看文档可能会增加一些时间成本，但是对比口头约定来讲会节省很多人力成本；

我们的开发团队就面临这样的问题，很多时候配置和系统的详细架构设计信息，只能依赖少部分人，于是这部分人不得不承担大部分系统问题的解答工作，严重影响了双方的工作效率，尽管把开发设计、架构信息文档化很麻烦，但是梳理后的配置文档信息会节约很多时间。



## 🛸开源项目

#### [moffee](https://github.com/BMPixel/moffee)

开源的markdown制作ppt工具，支持自动分页和样式设置，可以通过网页实时页面预览或导出PPT。



#### [developer2gwy](https://github.com/miss-mumu/developer2gwy)

开源项目程序员考公指南，介绍作者从备考到上岸的经历以及一些经验的分享，不过项目很久没有更新了，部分链接也打不开，只能作为参考信息。类似的项目还有这个 [coder2gwy](https://github.com/coder2gwy/coder2gwy)



## 🚀网站&工具

#### [freaky font generator](https://freakyfontgenerator.top/)

一款在线字体生成工具，通过Unicode字符编码转换，可以生成各种有趣效果的字体，生成的字体支持一键复制。



#### [aichatru](https://aichatru.ru/zh-CN)

免费的AI在线聊天工具，目前支持GPT-4o和Claude3，无需登陆可以直接发起会话。



## ⛵资料&博文

#### [comprehensive-rust](https://google.github.io/comprehensive-rust/)

Google安卓团队开源的Rust教程，可以帮你做Rust的基础知识入门，大厂出品的课程质量还是有保证的，推荐看看。



#### [cs224n](https://web.stanford.edu/class/cs224n/)

斯坦福大学2024年NLP公开课程，实用性和更新都比较好，推荐感兴趣的同学看看。



#### [putting the you in CPU](https://cpu.land/)

一本英文科普书，帮你理解处理器工作原理和系统调用相关的知识点。



#### [union-intersection-difference-javascript-sets](https://www.sonarsource.com/blog/union-intersection-difference-javascript-sets/)

关于JS即将引入的新功能，增强set集合的操作功能，支持两个集合之间求并集、交集、差集功能的介绍，目前该功能已经被chrome-122版本支持。



#### [git worktree](https://fev.al/posts/git-worktree/)

关于git命令`worktree`的介绍，可以实现同一分支下创建不同的工作目录操作。