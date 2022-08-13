# -*- coding: utf-8 -*-
"""
Created on Tue Nov 12 21:06:28 2019

@author: zjy
"""

# 先引入后面可能用到的包（package）
import pandas as pd
import numpy as np
from pyecharts.charts import Kline, Line, Bar, Grid
from pyecharts.commons.utils import JsCode
from zvt.domain import Index1dKdata
# 正常显示画图时出现的中文和负号
from pylab import mpl
from pyecharts import options as opts

mpl.rcParams['font.sans-serif'] = ['SimHei']
mpl.rcParams['axes.unicode_minus'] = False

# 常用大盘指数
indexs = {'上证综指': '000001.SH', '深证成指': '399001.SZ', '沪深300': '000300.SH',
          '创业板指': '399006.SZ', '上证50': '000016.SH', '中证500': '000905.SH',
          '中小板指': '399005.SZ', '上证180': '000010.SH'}

def plot_kline_volume_signal(data):
    kline = (
        Kline(init_opts=opts.InitOpts(width="1800px", height="1000px"))
            .add_xaxis(xaxis_data=list(data.index))
            .add_yaxis(
            series_name="klines",
            y_axis=data[["open", "close", "low", "high"]].values.tolist(),
            itemstyle_opts=opts.ItemStyleOpts(color="#ec0000", color0="#00da3c"),
        )
            .set_global_opts(legend_opts=opts.LegendOpts(is_show=True, pos_bottom=10, pos_left="center"),
                             datazoom_opts=[
                                 opts.DataZoomOpts(
                                     is_show=False,
                                     type_="inside",
                                     xaxis_index=[0, 1],
                                     range_start=98,
                                     range_end=100,
                                 ),
                                 opts.DataZoomOpts(
                                     is_show=True,
                                     xaxis_index=[0, 1],
                                     type_="slider",
                                     pos_top="85%",
                                     range_start=98,
                                     range_end=100,
                                 ),
                             ],
                             yaxis_opts=opts.AxisOpts(
                                 is_scale=True,
                                 splitarea_opts=opts.SplitAreaOpts(
                                     is_show=True, areastyle_opts=opts.AreaStyleOpts(opacity=1)
                                 ),
                             ),
                             tooltip_opts=opts.TooltipOpts(
                                 trigger="axis",
                                 axis_pointer_type="cross",
                                 background_color="rgba(245, 245, 245, 0.8)",
                                 border_width=1,
                                 border_color="#ccc",
                                 textstyle_opts=opts.TextStyleOpts(color="#000"),
                             ),
                             visualmap_opts=opts.VisualMapOpts(
                                 is_show=False,
                                 dimension=2,
                                 series_index=5,
                                 is_piecewise=True,
                                 pieces=[
                                     {"value": 1, "color": "#00da3c"},
                                     {"value": -1, "color": "#ec0000"},
                                 ],
                             ),
                             axispointer_opts=opts.AxisPointerOpts(
                                 is_show=True,
                                 link=[{"xAxisIndex": "all"}],
                                 label=opts.LabelOpts(background_color="#777"),
                             ),
                             brush_opts=opts.BrushOpts(
                                 x_axis_index="all",
                                 brush_link="all",
                                 out_of_brush={"colorAlpha": 0.1},
                                 brush_type="lineX",
                             ),
                             )
    )

    bar = (
        Bar()
            .add_xaxis(xaxis_data=list(data.index))
            .add_yaxis(
            series_name="volume",
            y_axis=data["volume"].tolist(),
            xaxis_index=1,
            yaxis_index=1,
            label_opts=opts.LabelOpts(is_show=False),
            itemstyle_opts=opts.ItemStyleOpts(
                color=JsCode(
                    """
                function(params) {
                    var colorList;
                    if (barData[params.dataIndex][1] > barData[params.dataIndex][0]) {
                        colorList = '#ef232a';
                    } else {
                        colorList = '#14b143';
                    }
                    return colorList;
                }
                """
                )
            ),
        )
            .set_global_opts(
            xaxis_opts=opts.AxisOpts(
                type_="category",
                grid_index=1,
                axislabel_opts=opts.LabelOpts(is_show=False),
            ),
            legend_opts=opts.LegendOpts(is_show=False),
        )
    )

    line = (Line()
        .add_xaxis(xaxis_data=list(data.index))
        .add_yaxis(
        series_name="ma5",
        y_axis=data["ma5"].tolist(),
        xaxis_index=1,
        yaxis_index=1,
        label_opts=opts.LabelOpts(is_show=False),
    # ).add_yaxis(
    #     series_name="ma10",
    #     y_axis=data["ma10"].tolist(),
    #     xaxis_index=1,
    #     yaxis_index=1,
    #     label_opts=opts.LabelOpts(is_show=False),
    ).add_yaxis(
        series_name="ma20",
        y_axis=data["ma20"].tolist(),
        xaxis_index=1,
        yaxis_index=1,
        label_opts=opts.LabelOpts(is_show=False),
    )
    )

    grid_chart = Grid(
        init_opts=opts.InitOpts(
            width="1800px",
            height="1000px",
            animation_opts=opts.AnimationOpts(animation=False),
        )
    )

    grid_chart.add_js_funcs("var barData={}".format(data[["open", "close"]].values.tolist()))
    overlap_kline_line = kline.overlap(line)
    grid_chart.add(
        overlap_kline_line,
        # kline,
        grid_opts=opts.GridOpts(pos_left="11%", pos_right="8%", height="40%"),
    )
    grid_chart.add(
        bar,
        grid_opts=opts.GridOpts(
            pos_left="10%", pos_right="8%", pos_top="60%", height="20%"
        ),
    )
    # grid_chart.render("kline_volume_signal.html")
    return  grid_chart

class Index_data(object):
    def __init__(self, name, n=100):
        self.name = name
        self.n = n

    def get_index_data(self):
        code = indexs[self.name]
        df = Index1dKdata.query_data(codes=[code[:6]],
                                     limit=self.n,
                                     order=Index1dKdata.timestamp.desc()
                                     )
        df.index = pd.to_datetime(df.timestamp)
        df = (df.sort_index()).drop('timestamp', axis=1)
        return df[-self.n:]

    def cal_hadata(self):
        df = self.get_index_data()
        # 计算修正版K线
        df['ha_close'] = (df.close + df.open + df.high + df.low) / 4.0
        ha_open = np.zeros(df.shape[0])
        ha_open[0] = df.open[0]
        for i in range(1, df.shape[0]):
            ha_open[i] = (ha_open[i - 1] + df['ha_close'][i - 1]) / 2
        df.insert(1, 'ha_open', ha_open)
        df['ha_high'] = df[['high', 'ha_open', 'ha_close']].max(axis=1)
        df['ha_low'] = df[['low', 'ha_open', 'ha_close']].min(axis=1)
        df = df.iloc[1:]
        return df

    def kline_plot(self, ktype=0):
        df = self.cal_hadata()
        # 画K线图数据
        date = df.index.strftime('%Y-%m-%d').tolist()
        if ktype == 0:
            k_value = df[['open', 'close', 'low', 'high','volume']]
        else:
            k_value = df[['ha_open', 'ha_close', 'ha_low', 'ha_high','volume']]
        # 引入pyecharts画图使用的是0.5.11版本，新版命令需要重写
        # 加入5、20日均线
        k_value['ma20'] = df.close.rolling(20).mean()
        k_value['ma5'] = df.close.rolling(5).mean()
        grid_chart = plot_kline_volume_signal(k_value)
        return grid_chart


if __name__ == '__main__':
    df = Index_data('上证综指').kline_plot(ktype=0)
    df.render("上证综指.html")