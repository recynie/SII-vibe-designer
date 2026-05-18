# Skill · Logo（介质工艺手册）

Logo 介质：1024×1024 PNG，1:1，flat vector 风。

## 工艺要点
- gen_image prompt 用全英文，结构 `<主体> + <关键词> + <配色> + <构图> + <质感>`
- 颜色强约束：`STRICTLY use only #X for X, #Y for Y - NO other colors, NO color shifts`
- 末尾必加：`flat vector, scalable, on solid background, no gradients, no emoji, no photorealistic textures, no faces`
- 中文品牌：写 `containing the Chinese characters "<名>"`，不要让模型自己生中文（90% 出错字）

## 反 slop 红线
- 假国际范装饰（星月、emoji 风插图）
- 细密线条（vector 后糊）
- 写实材质（金属/玻璃质感）——这是渲染图不是 logo
- Inter / Arial 当 display
