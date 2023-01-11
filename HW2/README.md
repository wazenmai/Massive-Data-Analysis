# HW2 - PageRank

此專案以 MapReduce 的架構來實作 PageRank 的計算，除了輸入輸出，其餘都是用 pyspark 提供的 function 完成。
- input: `input.txt`，每一行都是一條 link (\<source\> \<destination\>)


- output: 前十個 PageRank 最高的點 (\<node\> \<rank\>)

## 步驟說明
### Preprocess
1. `lines` : 把檔案讀進來用 `map` 變成 (\<source\>, \<destination\>) 的形式。


2. 找出 node 總數 $N$: 利用 `map` 將 source 跟 destination 的點分開，再搭配 `union` 跟 `distinct` 可以得到所有的點 ID，最後用 `count` 算出 $N$。


3. 找出 **lonelyNode** : 在測試自己生的小測資時發現沒有 in-link 的點會隨著計算慢慢消失，解法為用 `subtract` 找出那些只存在 source 卻不存在於 destination 的 node，每次計算時都加一條到接到自己、weight = 0 的 link。


4. `links` : 把 `lines` 用 `map` 變成 (\<source\>, [\<destination1\, \<destination2\>...]) 的形式。


5. `ranks` : 代表各個 node 的 PageRank 分數，一開始每個點的分數都是 $1/N$。

### Computation （loop）
將下面這些步驟重複計算 20 次
1. `weights` : 算出經過一次計算後各個 source node 給 destination node 的 PageRank 值。
    - `links.join(ranks)`: 得到 (\<source\>, ([\<destination1\, \<destination2\>...], \<rank\>))。
    - `flatMap(lambda x: computeWeights(x[1][0], x[1][1]))` : 透過 `computeWeight` 計算 $\beta$ * rank / len(destination)。
  
    
2. `ranks`-v1: 用 `reduceByKey` 把 `weights` 中同個 node 的分數加總，再透過 `union` 加上 `lonelyNode` 的分數。


3. $S$: 根據下方公式，$\sum r'^{new}_j$ 就是目前 `ranks` 的分數加總，可直接用 `sum` 得到。
    $$\forall j:r^{new}_j=r'^{new}_j+\frac{1-S}{N}  \qquad \text{where}:S=\sum r'^{new}_j$$
 
 
4. `ranks`-v2: 因為不會動到 key，所以直接用 `mapValues` 把 PageRank 的分數直接加上 $(1 - S)/N$。

### Output
計算完畢後，用 `sortBy` 讓 `ranks` 的分數可以由大到小排，取前十項用 `%f` 輸出即為答案。