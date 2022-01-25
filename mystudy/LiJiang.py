from multiprocessing import Process, JoinableQueue
import time

t0 = time.time()


# 消费者方法
def consumer(q, name):
    while True:
        res = q.get()
        if res is None:
            break
        t = time.time() - t0
        print('time: {:.2f}, {:s} 处理了 {:s}'.format(t, name, res))
        time.sleep(10)  # 模拟葫芦娃处理数据的时间
        q.task_done()  # 发送信号给q.join(),表示已经从队列中取走一个值并处理完毕了


# 生产者方法
def producer(q, name, udp):
    for i in range(20):
        res = '{:s} {:d}'.format(udp, i)  # 小礼这下牛比了，疯狂在这里读udp
        time.sleep(1)  # 模拟小礼读到的时间延迟
        t = time.time() - t0
        print('time: {:.2f}, {:s} 读到了 {:s}'.format(t, name, res))
        q.put(res)  # 把读取的udp放入到队列中
    q.join()  # 等消费者把自己放入队列的所有元素取完之后才结束


if __name__ == "__main__":
    q = JoinableQueue()
    # 创建生产者
    p1 = Process(target=producer, args=(q, '礼ちゃん', 'udp'))
    # 创建消费者
    c1 = Process(target=consumer, args=(q, '大娃',))
    c2 = Process(target=consumer, args=(q, '二娃',))
    c3 = Process(target=consumer, args=(q, '三娃',))
    c4 = Process(target=consumer, args=(q, '四娃',))
    c5 = Process(target=consumer, args=(q, '五娃',))
    c6 = Process(target=consumer, args=(q, '六娃',))
    c7 = Process(target=consumer, args=(q, '七娃',))

    c1.daemon = True
    c2.daemon = True
    c3.daemon = True
    c4.daemon = True
    c5.daemon = True
    c6.daemon = True
    c7.daemon = True

    p_l = [p1, c1, c2, c3, c4, c5, c6, c7]
    for p in p_l:
        p.start()

    p1.join()
    print('葫芦娃救爷爷')
