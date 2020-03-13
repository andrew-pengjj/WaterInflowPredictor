# -*- coding:utf-8 -*-

from pandas import read_csv, DataFrame
from numpy import array
import math
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression


class doubleexp:
    def __init__(self, filename="data/test_data2.csv"):
        self.A1_weight = [14.125547, 20.335546, 3427.019928, -64245.986398, -18916.128418, -26.764629, -7.789837,
                          1.791363, 76.886520]
        self.A2_weight = [11.459442, 20.649642, 583.598444, -35351.470635, -13776.980845, -10.384708, -9.621880,
                          1.788100, 182.870755]
        self.k1_weight = [-0.001309, 0.008579, -0.939159, -5.930224, -3.377775, -0.023162, -0.002060, 0.000831,
                          0.283855]
        self.k2_weight = [-0.000588, 0.060149, 7.949096, -56.232117, -50.203916, -0.001170, -0.027725, 0.009435,
                          0.493273]
        self.C_weight = [0.272010, 0.784499, 166.725320, -2175.109151, -969.975456, -1.628561, -0.016964, 0.110913,
                         1.598855]
        self.flag = 0
        if not filename:
            self.x = [i * 0.05 for i in range(400)]
            self.y = [i * 0.05 for i in range(400)]
        else:
            self.flag = 1
            df = read_csv(filename)
            self.x = list(df['x'])
            self.y = list(df['y'])

    def pointmulti(self, listA, listB):
        result = 0
        for i in range(len(listA)):
            result += listA[i] * listB[i]
        return result

    def cal_dexp_data(self, A1, A2, k1, k2, C, item):
        return A1 * math.exp(-k1 * item) - A2 * math.exp(-k2 * item) + C

    def cal_dexp_derivative(slef, A1, A2, k1, k2, item):
        return -A1 * k1 * math.exp(-k1 * item) + A2 * k2 * math.exp(-k2 * item)

    def JLoss(self, A1, A2, k1, k2, C):
        try:
            y_pred = [self.cal_dexp_data(A1, A2, k1, k2, C, item) for item in self.x]
            return math.sqrt(sum([(y_pred[i] - self.y[i]) ** 2 for i in range(len(self.x))]) / float(len(self.x)))
        except:
            return float("inf")

    def default_update_fit(self, H, M, K, mu, q, W, Hf, D, V):
        ret = 0  # 为0则表示更新失败
        input_data = [H]
        input_data.append(M)
        input_data.append(K)
        input_data.append(mu)
        input_data.append(q)
        input_data.append(W)
        input_data.append(Hf)
        input_data.append(D)
        input_data.append(V)
        if len(input_data) != len(self.A1_weight):
            print("参数个数不对，长度不等于9")
            return ret, 0, 0, 0, 0, 0
        else:
            ret = 1
            A1 = self.pointmulti(input_data, self.A1_weight)
            A2 = self.pointmulti(input_data, self.A2_weight)
            k1 = self.pointmulti(input_data, self.k1_weight)
            k2 = self.pointmulti(input_data, self.k2_weight)
            C = self.pointmulti(input_data, self.C_weight)
            return ret, A1, A2, k1, k2, C

    def linearopt(self, k1, k2):
        A1_x = [math.exp(-k1 * item) for item in self.x]
        A2_x = [-math.exp(-k2 * item) for item in self.x]
        df = DataFrame({"A1_x": A1_x, "A2_x": A2_x, "y": self.y})
        # 建立线性回归模型
        indep = df[["A1_x", "A2_x"]]
        dep = df["y"]
        indep = array(indep).reshape(-1, 2)
        dep = array(dep).reshape(-1, 1)
        model = LinearRegression(fit_intercept=True)
        model.fit(indep, dep)
        A1 = model.coef_[0][0]
        A2 = model.coef_[0][1]
        C = model.intercept_[0]
        if A1 < 0 and A2 < 0:
            tmp = A1
            A1 = -A2
            A2 = -tmp
            tmp = k1
            k1 = k2
            k2 = tmp
        jloss = self.JLoss(A1, A2, k1, k2, C)
        # print("method << Least square >>, A1=%0.3f, A2=%0.3f, k1 =%0.3f, k2 =%0.3f, C=%0.3f, JLOSS = %0.4f \n"%(A1,A2,k1,k2,C,jloss))
        return A1, A2, k1, k2, C, jloss

    def find_best_k(self, k1_list, k2_list):
        JLOSS = []
        for k1 in k1_list:
            for k2 in k2_list:
                A1_new, A2_new, k1_new, k2_new, C_new, jloss = self.linearopt(k1, k2)
                JLOSS.append((k1_new, k2_new, A1_new, A2_new, C_new, jloss))
        # 寻找最优的 k1,k2
        jloss = array([item[5] for item in JLOSS])
        bb = jloss.tolist()
        index = bb.index(min(bb))
        k1 = JLOSS[index][0]
        k2 = JLOSS[index][1]
        A1 = JLOSS[index][2]
        A2 = JLOSS[index][3]
        C = JLOSS[index][4]
        loss = JLOSS[index][5]
        return k1, k2, A1, A2, C, loss

    def find_best_outloop(self, k1_init=0, k2_init=0, out_precision=0):
        k1_max = 6
        k2_max = 6
        k1_min = 0
        k2_min = 0
        k1_interval = []
        k2_interval = []
        if out_precision == 0:
            interval_num = 30
            k1_interval.extend([(k1_max - k1_min) / float(interval_num) * i for i in range(interval_num + 1)])
            k2_interval.extend([(k2_max - k2_min) / float(interval_num) * i for i in range(interval_num + 1)])
            k1, k2, A1, A2, C, loss = self.find_best_k(k1_interval, k2_interval)
            print("out_precision=%d, k1=%0.3f, k2=%0.3f, A1=%0.3f, A2=%0.3f, C=%0.3f, loss=%0.3f" % (
            out_precision, k1, k2, A1, A2, C, loss))
            return k1, k2, A1, A2, C
        elif out_precision == 1:
            interval_num = 10
            k1_min = max(k1_init - 0.05, 0)
            k2_min = max(k2_init - 0.05, 0)
            k1_max = min(k1_init + 0.05, 8)
            k2_max = min(k2_init + 0.05, 8)
            k1_interval.extend([k1_min + (k1_max - k1_min) / float(interval_num) * i for i in range(interval_num + 1)])
            k2_interval.extend([k2_min + (k2_max - k2_min) / float(interval_num) * i for i in range(interval_num + 1)])
            k1, k2, A1, A2, C, loss = self.find_best_k(k1_interval, k2_interval)
            print("out_precision=%d, k1=%0.3f, k2=%0.3f, A1=%0.3f, A2=%0.3f, C=%0.3f, loss=%0.3f" % (
            out_precision, k1, k2, A1, A2, C, loss))
            return k1, k2, A1, A2, C
        else:
            interval_num = 10
            k1_min = max(k1_init - 0.01, 0)
            k2_min = max(k2_init - 0.01, 0)
            k1_max = min(k1_init + 0.01, 8)
            k2_max = min(k2_init + 0.01, 8)
            k1_interval.extend([k1_min + (k1_max - k1_min) / float(interval_num) * i for i in range(interval_num + 1)])
            k2_interval.extend([k2_min + (k2_max - k2_min) / float(interval_num) * i for i in range(interval_num + 1)])
            k1, k2, A1, A2, C, loss = self.find_best_k(k1_interval, k2_interval)
            print("out_precision=%d, k1=%0.3f, k2=%0.3f, A1=%0.3f, A2=%0.3f, C=%0.3f, loss=%0.3f" % (
            out_precision, k1, k2, A1, A2, C, loss))
            return k1, k2, A1, A2, C

    def find_best_parameter(self):
        k1 = 0
        k2 = 0
        A1 = 0
        A2 = 0
        C = 0
        for i in range(3):
            k1, k2, A1, A2, C = self.find_best_outloop(k1, k2, i)
        return A1, A2, k1, k2, C

    def find_key_point(self, x_list, A1, A2, k1, k2, C):
        # 计算高峰的峰值
        error = 0.05
        high_ratio = round(math.log(float(A1 * k1) / (A2 * k2)) / float(k1 - k2),4)
        high_volume = round(self.cal_dexp_data(A1, A2, k1, k2, C, high_ratio),4)
        y_d = [abs(self.cal_dexp_derivative(A1, A2, k1, k2, item) - error) for item in x_list]
        balance_id = len(y_d) - 1
        for i in range(len(y_d)):
            if y_d[i] <= error and x_list[i] >= high_ratio + 0.5:
                balance_id = i
                break
        balance_ratio = round(x_list[balance_id],4)
        balance_volume = round(self.cal_dexp_data(A1, A2, k1, k2, C, balance_ratio),4)
        keyvalue_dict = {"balance_ratio": balance_ratio, "balance_volume": balance_volume, "high_ratio": high_ratio,
                         "high_volume": high_volume}
        return keyvalue_dict

    def plot_dexp_data(self, H, M, K, mu, q, W, Hf, D, V, path):
        A1 = 3189.00
        A2 = 3212.87
        k1 = 0.68
        k2 = 0.473
        C = 49.47
        ret = 0
        if self.flag == 1:
            A1, A2, k1, k2, C = self.find_best_parameter()
        else:
            ret, A1, A2, k1, k2, C = self.default_update_fit(H, M, K, mu, q, W, Hf, D, V)
        para_dict = {"A1": A1, "A2": A2, "k1": k1, "k2": k2, "C": C}
        para_dict['k1'] = round(para_dict['k1'], 4)
        para_dict['k2'] = round(para_dict['k2'], 4)
        x_min = min(self.x)
        x_max = max(self.x) + 2
        interval_num = 100
        x = [x_min + i * (x_max - x_min) / float(interval_num) for i in range(interval_num + 1)]
        y = [self.cal_dexp_data(A1, A2, k1, k2, C, item) for item in x]

        keyvalue_dict = self.find_key_point(x, A1, A2, k1, k2, C)
        plt.figure(figsize=(6, 4), dpi=200)
        plt.clf()
        if self.flag == 0:
            plt.plot(x, y, 'r', ls="--", lw=2, label="init curve")
            plt.legend(numpoints=1)
            plt.xlabel('ratio')
            plt.ylabel('Water inflow speed')
            plt.legend()
        else:
            plt.plot(self.x, self.y, color='blue', ls="-", lw=2, label="original curve")
            plt.plot(x, y, color='red', ls="-", lw=2, label="fit curve")
            plt.xlabel('ratio')
            plt.ylabel('Water inflow speed')
            plt.legend(numpoints=1)
        # plt.show()
        plt.savefig(path, dpi=65)
        return ret, para_dict, keyvalue_dict
