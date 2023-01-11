# HW1 - Matrix Multiplication


此專案以 MapReduce 的架構來實作矩陣相乘任務，除了輸入輸出，其餘都是用 pyspark 提供的 function 完成。
- input: `input.txt`，包含兩個矩陣 M, N。每行由{矩陣代號},{row number},{column number},{value} 組成
- output: 為答案矩陣 P。每行由 {row number},{column number},{value} 組成

### 概念說明：
    
1. 先把矩陣 M, N 分開存成兩個 RDD，變成分開的 $(j, (i, val_M))$ 和 $(j, (k, val_N))$
2. 接著從 M, N 各挑一個同樣的 key 的 pair 合併，變成 $(j, ((i, val_M), (k, val_N)))$ 
3. 把值相乘，key 改成答案矩陣的 (row number, column number) -> $((i, k), val_M * val_N)$
4. 把同一格的相加，排序整理，即為最終答案

**Flow**: `map` -> `filter`(`map` -> `reduce`) -> `map` -> `join` (`reduce`) -> `map` -> `reduce`

### 實作步驟：
1. 首先建立一個包含 application 資訊的 SparkConf，並藉此建立 SparkContext 來連到 cluster
2. 讀入檔案，利用 `map` 把每個 element 分開並存成 list
3. 利用 `filter` 把 M, N 矩陣分成兩個 RDD  (`filter` 為一次 `map` + 一次 `reduce`，首先把符合條件的 ele `map` 成（ele,ele)，再用 `reduce` 輸出 output)
4. 分別把 M, N `map` 成 $(j, (i, val_M))$ 和 $(j, (k, val_N))$ 的 key-value pair，因為矩陣相乘時 $j$ 一樣的值一定會乘在一起。 
5. 把相同 key 但在不同矩陣上的 pair 合併起來，這樣之後要相乘的值就能在同個 key-value pair 裡。`join` 可以把兩個 RDD key 相符的 pair 合在一起，變成 $(j, ((i, val_M), (k, val_N)))$ 由此我們得到 RDD `P`
6. 再用 `map` 把 `P` 裡的 key-value pair 變成 $((i,k), val_M * val_N)$
7. 接下來就可以利用 `reduceByKey` 把同個 key 的 value 加起來並輸出
8. 使用 `sortByKey` 讓 key-value pair 的排列方式與 input 一致，default 為 ascending order
9. 使用 `collect()` 把 RDD 轉回 python list，輸出 `output.txt`
10. `sc.stop()` 停止 SparkContext 服務
