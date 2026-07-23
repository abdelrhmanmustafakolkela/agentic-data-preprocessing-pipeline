import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import base64
import io
from typing import Dict, Any, List, Optional
import logging

logger = logging.getLogger(__name__)

sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (10, 6)


def render_to_base64(fig: plt.Figure) -> str:
    buf = io.BytesIO()
    fig.savefig(buf, format='png', dpi=100, bbox_inches='tight')
    buf.seek(0)
    img_base64 = base64.b64encode(buf.read()).decode('utf-8')
    buf.close()
    plt.close(fig)
    return img_base64


def histogram(df: pd.DataFrame, spec: Dict[str, Any]) -> Optional[Dict[str, str]]:
    x = spec.get('x')
    if not x or x not in df.columns:
        logger.warning(f"Histogram: column '{x}' not found")
        return None
    if not pd.api.types.is_numeric_dtype(df[x]):
        logger.warning(f"Histogram: column '{x}' is not numeric")
        return None
    fig, ax = plt.subplots()
    ax.hist(df[x].dropna(), bins=30, edgecolor='black', alpha=0.7)
    ax.set_xlabel(x)
    ax.set_ylabel('Frequency')
    ax.set_title(spec.get('title', f'Histogram of {x}'))
    return {'title': spec.get('title', f'Histogram of {x}'), 'chart_type': 'histogram', 'image_base64': render_to_base64(fig)}


def bar(df: pd.DataFrame, spec: Dict[str, Any]) -> Optional[Dict[str, str]]:
    x = spec.get('x')
    y = spec.get('y')
    agg = spec.get('agg', 'mean')
    if not x or x not in df.columns:
        logger.warning(f"Bar chart: x column '{x}' not found")
        return None
    fig, ax = plt.subplots()
    if y and y in df.columns:
        if agg == 'sum':
            data = df.groupby(x)[y].sum()
        elif agg == 'mean':
            data = df.groupby(x)[y].mean()
        elif agg == 'count':
            data = df.groupby(x)[y].count()
        elif agg == 'median':
            data = df.groupby(x)[y].median()
        else:
            data = df.groupby(x)[y].mean()
        data.plot(kind='bar', ax=ax, edgecolor='black', alpha=0.7)
        ax.set_ylabel(y)
    else:
        df[x].value_counts().plot(kind='bar', ax=ax, edgecolor='black', alpha=0.7)
        ax.set_ylabel('Count')
    ax.set_xlabel(x)
    ax.set_title(spec.get('title', f'Bar Chart of {x}'))
    plt.xticks(rotation=45, ha='right')
    return {'title': spec.get('title', f'Bar Chart of {x}'), 'chart_type': 'bar', 'image_base64': render_to_base64(fig)}


def line(df: pd.DataFrame, spec: Dict[str, Any]) -> Optional[Dict[str, str]]:
    x = spec.get('x')
    y = spec.get('y')
    if not x or x not in df.columns:
        logger.warning(f"Line chart: x column '{x}' not found")
        return None
    if not y or y not in df.columns:
        logger.warning(f"Line chart: y column '{y}' not found")
        return None
    fig, ax = plt.subplots()
    ax.plot(df[x], df[y], marker='o', linewidth=2, markersize=4)
    ax.set_xlabel(x)
    ax.set_ylabel(y)
    ax.set_title(spec.get('title', f'Line Chart: {y} vs {x}'))
    return {'title': spec.get('title', f'Line Chart: {y} vs {x}'), 'chart_type': 'line', 'image_base64': render_to_base64(fig)}


def scatter(df: pd.DataFrame, spec: Dict[str, Any]) -> Optional[Dict[str, str]]:
    x = spec.get('x')
    y = spec.get('y')
    hue = spec.get('hue')
    if not x or x not in df.columns:
        logger.warning(f"Scatter plot: x column '{x}' not found")
        return None
    if not y or y not in df.columns:
        logger.warning(f"Scatter plot: y column '{y}' not found")
        return None
    fig, ax = plt.subplots()
    if hue and hue in df.columns:
        unique_hues = df[hue].unique()
        for hue_val in unique_hues[:10]:
            subset = df[df[hue] == hue_val]
            ax.scatter(subset[x], subset[y], label=str(hue_val), alpha=0.6)
        ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    else:
        ax.scatter(df[x], df[y], alpha=0.6)
    ax.set_xlabel(x)
    ax.set_ylabel(y)
    ax.set_title(spec.get('title', f'Scatter Plot: {y} vs {x}'))
    return {'title': spec.get('title', f'Scatter Plot: {y} vs {x}'), 'chart_type': 'scatter', 'image_base64': render_to_base64(fig)}


def box(df: pd.DataFrame, spec: Dict[str, Any]) -> Optional[Dict[str, str]]:
    x = spec.get('x')
    y = spec.get('y')
    fig, ax = plt.subplots()
    if y and y in df.columns:
        if x and x in df.columns:
            df.boxplot(column=y, by=x, ax=ax)
            ax.set_xlabel(x)
            ax.set_ylabel(y)
        else:
            ax.boxplot(df[y].dropna())
            ax.set_ylabel(y)
    elif x and x in df.columns:
        ax.boxplot(df[x].dropna())
        ax.set_ylabel(x)
    else:
        logger.warning("Box plot: need at least one numeric column")
        plt.close(fig)
        return None
    ax.set_title(spec.get('title', 'Box Plot'))
    if hasattr(fig, 'suptitle'):
        fig.suptitle('')
    return {'title': spec.get('title', 'Box Plot'), 'chart_type': 'box', 'image_base64': render_to_base64(fig)}


def correlation_heatmap(df: pd.DataFrame, spec: Dict[str, Any]) -> Optional[Dict[str, str]]:
    columns = spec.get('columns')
    if columns:
        numeric_cols = [col for col in columns if col in df.columns and pd.api.types.is_numeric_dtype(df[col])]
    else:
        numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
    if len(numeric_cols) < 2:
        logger.warning("Correlation heatmap: need at least 2 numeric columns")
        return None
    corr_matrix = df[numeric_cols].corr()
    fig, ax = plt.subplots(figsize=(10, 8))
    sns.heatmap(corr_matrix, annot=True, fmt='.2f', cmap='coolwarm', center=0, square=True, linewidths=1, ax=ax)
    ax.set_title(spec.get('title', 'Correlation Heatmap'))
    return {'title': spec.get('title', 'Correlation Heatmap'), 'chart_type': 'correlation_heatmap', 'image_base64': render_to_base64(fig)}


def pie(df: pd.DataFrame, spec: Dict[str, Any]) -> Optional[Dict[str, str]]:
    x = spec.get('x')
    if not x or x not in df.columns:
        logger.warning(f"Pie chart: column '{x}' not found")
        return None
    value_counts = df[x].value_counts().head(10)
    if len(value_counts) == 0:
        logger.warning(f"Pie chart: no data for column '{x}'")
        return None
    fig, ax = plt.subplots()
    ax.pie(value_counts.values, labels=value_counts.index, autopct='%1.1f%%', startangle=90)
    ax.set_title(spec.get('title', f'Pie Chart of {x}'))
    return {'title': spec.get('title', f'Pie Chart of {x}'), 'chart_type': 'pie', 'image_base64': render_to_base64(fig)}


def count_plot(df: pd.DataFrame, spec: Dict[str, Any]) -> Optional[Dict[str, str]]:
    x = spec.get('x')
    hue = spec.get('hue')
    if not x or x not in df.columns:
        logger.warning(f"Count plot: column '{x}' not found")
        return None
    fig, ax = plt.subplots(figsize=(10, 6))
    if hue and hue in df.columns:
        sns.countplot(data=df, x=x, hue=hue, ax=ax)
    else:
        sns.countplot(data=df, x=x, ax=ax)
    ax.set_title(spec.get('title', f'Count Plot of {x}'))
    plt.xticks(rotation=45, ha='right')
    return {'title': spec.get('title', f'Count Plot of {x}'), 'chart_type': 'count_plot', 'image_base64': render_to_base64(fig)}


CHART_DISPATCH = {"histogram": histogram, "bar": bar, "line": line, "scatter": scatter, "box": box, "correlation_heatmap": correlation_heatmap, "pie": pie, "count_plot": count_plot}


def generate_charts(df: pd.DataFrame, chart_plan: List[Dict[str, Any]]) -> List[Dict[str, str]]:
    charts = []
    for spec in chart_plan:
        chart_type = spec.get('chart_type')
        if chart_type not in CHART_DISPATCH:
            logger.warning(f"Unknown chart type: {chart_type}")
            continue
        try:
            func = CHART_DISPATCH[chart_type]
            chart_result = func(df, spec)
            if chart_result:
                chart_result['reason'] = spec.get('reason', '')
                charts.append(chart_result)
        except Exception as e:
            logger.error(f"Error generating {chart_type} chart: {str(e)}")
            continue
    return charts
