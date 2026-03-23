import numpy as np
import collections
import torch
from torch.autograd import Variable
import torch.optim as optim

import rnn

start_token = 'G'
end_token = 'E'
batch_size = 64

# ===== 自动检测并使用 GPU =====
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
print(f"Using device: {device}")


def process_poems1(file_name):
    """
    处理 poems.txt 格式：每行 "title:content"
    :return: poems_vector, word_int_map, words
    """
    poems = []
    with open(file_name, "r", encoding='utf-8') as f:
        for line in f.readlines():
            try:
                title, content = line.strip().split(':')
                content = content.replace(' ', '')
                if '_' in content or '(' in content or '（' in content or '《' in content or '[' in content or \
                                start_token in content or end_token in content:
                    continue
                if len(content) < 5 or len(content) > 80:
                    continue
                content = start_token + content + end_token
                poems.append(content)
            except ValueError:
                pass
    poems = sorted(poems, key=lambda line: len(line))
    all_words = []
    for poem in poems:
        all_words += [word for word in poem]
    counter = collections.Counter(all_words)
    count_pairs = sorted(counter.items(), key=lambda x: -x[1])
    words, _ = zip(*count_pairs)
    words = words[:len(words)] + (' ',)
    word_int_map = dict(zip(words, range(len(words))))
    poems_vector = [list(map(word_int_map.get, poem)) for poem in poems]
    return poems_vector, word_int_map, words


def process_poems2(file_name):
    """
    处理 tangshi.txt 格式：每行为一段诗句（无 title: 前缀）
    :return: poems_vector, word_int_map, words
    """
    poems = []
    with open(file_name, "r", encoding='utf-8') as f:
        for line in f.readlines():
            try:
                line = line.strip()
                if line:
                    content = line.replace('\u2018', '').replace('\u2019', '').replace('，', '').replace('。', '')
                    if '_' in content or '(' in content or '（' in content or '《' in content or '[' in content or \
                                    start_token in content or end_token in content:
                        continue
                    if len(content) < 5 or len(content) > 80:
                        continue
                    content = start_token + content + end_token
                    poems.append(content)
            except ValueError:
                pass
    poems = sorted(poems, key=lambda line: len(line))
    all_words = []
    for poem in poems:
        all_words += [word for word in poem]
    counter = collections.Counter(all_words)
    count_pairs = sorted(counter.items(), key=lambda x: -x[1])
    words, _ = zip(*count_pairs)
    words = words[:len(words)] + (' ',)
    word_int_map = dict(zip(words, range(len(words))))
    poems_vector = [list(map(word_int_map.get, poem)) for poem in poems]
    return poems_vector, word_int_map, words


def process_poems_combined(file1, file2):
    """
    同时使用两个数据集 (poems.txt + tangshi.txt)，合并后统一建词表。
    :return: poems_vector, word_int_map, words
    """
    poems = []

    # ---- 读取 poems.txt (title:content 格式) ----
    with open(file1, "r", encoding='utf-8') as f:
        for line in f.readlines():
            try:
                title, content = line.strip().split(':')
                content = content.replace(' ', '')
                if '_' in content or '(' in content or '（' in content or '《' in content or '[' in content or \
                                start_token in content or end_token in content:
                    continue
                if len(content) < 5 or len(content) > 80:
                    continue
                poems.append(start_token + content + end_token)
            except ValueError:
                pass

    # ---- 读取 tangshi.txt (每行一段诗句) ----
    with open(file2, "r", encoding='utf-8') as f:
        for line in f.readlines():
            try:
                line = line.strip()
                if line:
                    content = line.replace('\u2018', '').replace('\u2019', '').replace('，', '').replace('。', '')
                    if '_' in content or '(' in content or '（' in content or '《' in content or '[' in content or \
                                    start_token in content or end_token in content:
                        continue
                    if len(content) < 5 or len(content) > 80:
                        continue
                    poems.append(start_token + content + end_token)
            except ValueError:
                pass

    # ---- 统一排序 & 建词表 ----
    poems = sorted(poems, key=lambda line: len(line))
    all_words = []
    for poem in poems:
        all_words += [word for word in poem]
    counter = collections.Counter(all_words)
    count_pairs = sorted(counter.items(), key=lambda x: -x[1])
    words, _ = zip(*count_pairs)
    words = words[:len(words)] + (' ',)
    word_int_map = dict(zip(words, range(len(words))))
    poems_vector = [list(map(word_int_map.get, poem)) for poem in poems]
    return poems_vector, word_int_map, words


def generate_batch(batch_size, poems_vec, word_to_int):
    n_chunk = len(poems_vec) // batch_size
    x_batches = []
    y_batches = []
    for i in range(n_chunk):
        start_index = i * batch_size
        end_index = start_index + batch_size
        x_data = poems_vec[start_index:end_index]
        y_data = []
        for row in x_data:
            y = row[1:]
            y.append(row[-1])
            y_data.append(y)
        """
        x_data             y_data
        [6,2,4,6,9]       [2,4,6,9,9]
        [1,4,2,8,5]       [4,2,8,5,5]
        """
        x_batches.append(x_data)
        y_batches.append(y_data)
    return x_batches, y_batches


def run_training():
    # 同时使用两个数据集训练
    poems_vector, word_to_int, vocabularies = process_poems_combined('./poems.txt', './tangshi.txt')
    # 若只想用单个数据集，可改为：
    # poems_vector, word_to_int, vocabularies = process_poems1('./poems.txt')
    # poems_vector, word_to_int, vocabularies = process_poems2('./tangshi.txt')

    print("finish loading data, vocab size:", len(word_to_int))
    BATCH_SIZE = 100

    torch.manual_seed(5)
    word_emb = rnn.word_embedding(vocab_length=len(word_to_int) + 1, embedding_dim=100)
    rnn_model = rnn.RNN_model(
        batch_sz=BATCH_SIZE,
        vocab_len=len(word_to_int) + 1,
        word_embedding=word_emb,
        embedding_dim=100,
        lstm_hidden_dim=128
    ).to(device)  # 将模型移到 GPU/CPU

    optimizer = optim.RMSprop(rnn_model.parameters(), lr=0.01)
    loss_fun = torch.nn.NLLLoss()
    # 如已有训练好的模型，可取消下一行注释直接加载：
    # rnn_model.load_state_dict(torch.load('./poem_generator_rnn', map_location=device, weights_only=True))

    for epoch in range(30):
        batches_inputs, batches_outputs = generate_batch(BATCH_SIZE, poems_vector, word_to_int)
        n_chunk = len(batches_inputs)
        for batch in range(n_chunk):
            batch_x = batches_inputs[batch]
            batch_y = batches_outputs[batch]  # (batch, time_step)

            loss = 0
            for index in range(BATCH_SIZE):
                x = np.array(batch_x[index], dtype=np.int64)
                y = np.array(batch_y[index], dtype=np.int64)
                # 将张量移到 GPU/CPU
                x = Variable(torch.from_numpy(np.expand_dims(x, axis=1))).to(device)
                y = Variable(torch.from_numpy(y)).to(device)
                pre = rnn_model(x)
                loss += loss_fun(pre, y)
                if index == 0:
                    _, pre_idx = torch.max(pre, dim=1)
                    print('prediction', pre_idx.data.tolist())
                    print('b_y       ', y.data.tolist())
                    print('*' * 30)
            loss = loss / BATCH_SIZE
            print("epoch", epoch, 'batch number', batch, "loss is:", loss.data.tolist())
            optimizer.zero_grad()
            loss.backward()
            torch.nn.utils.clip_grad_norm_(rnn_model.parameters(), 1)
            optimizer.step()

            if batch % 20 == 0:
                # 保存时先移回 CPU，保证加载时不依赖 GPU 环境
                torch.save(rnn_model.cpu().state_dict(), './poem_generator_rnn')
                rnn_model.to(device)  # 保存后移回 GPU 继续训练
                print("finish save model")


def to_word(predict, vocabs):  # 预测的结果转化成汉字
    sample = np.argmax(predict)
    if sample >= len(vocabs):
        sample = len(vocabs) - 1
    return vocabs[sample]


def pretty_print_poem(poem):  # 令打印的结果更工整
    shige = []
    for w in poem:
        if w == start_token or w == end_token:
            break
        shige.append(w)
    poem_str = ''.join(shige)
    poem_sentences = poem_str.split('。')
    for s in poem_sentences:
        if s != '' and len(s) > 5:
            print(s + '。')


def gen_poem(begin_word):
    # 使用与训练相同的数据集
    poems_vector, word_int_map, vocabularies = process_poems_combined('./poems.txt', './tangshi.txt')

    word_emb = rnn.word_embedding(vocab_length=len(word_int_map) + 1, embedding_dim=100)
    rnn_model = rnn.RNN_model(
        batch_sz=64,
        vocab_len=len(word_int_map) + 1,
        word_embedding=word_emb,
        embedding_dim=100,
        lstm_hidden_dim=128
    )
    # weights_only=True 消除 FutureWarning；map_location='cpu' 兼容无 GPU 环境
    rnn_model.load_state_dict(torch.load('./poem_generator_rnn', map_location='cpu', weights_only=True))
    rnn_model.eval()
    # 生成阶段在 CPU 上跑即可，序列短，速度无差别

    # 以 start_token + begin_word 作为初始输入，确保生成诗句严格以 begin_word 开头
    poem = start_token + begin_word
    word = begin_word
    while word != end_token:
        input_vec = np.array([word_int_map[w] for w in poem], dtype=np.int64)
        input_tensor = Variable(torch.from_numpy(input_vec))
        output = rnn_model(input_tensor, is_test=True)
        word = to_word(output.data.tolist()[-1], vocabularies)
        poem += word
        if len(poem) > 32:  # start_token 占1位，故上限+2
            break
    return poem[1:]  # 去掉开头的 start_token 再返回


# ===== 训练 =====
run_training()  # 训练完成后请注释掉此行，直接运行生成部分

# ===== 生成诗歌（按 README 要求：日、红、山、夜、湖、海、月）=====
pretty_print_poem(gen_poem("日"))
pretty_print_poem(gen_poem("红"))
pretty_print_poem(gen_poem("山"))
pretty_print_poem(gen_poem("夜"))
pretty_print_poem(gen_poem("湖"))
pretty_print_poem(gen_poem("海"))
pretty_print_poem(gen_poem("月"))
