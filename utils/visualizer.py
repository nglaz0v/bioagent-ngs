import re
import io
import contextlib
import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from typing import List, Dict, Optional

def is_visualization_code(code: str) -> bool:
    """Проверяет, содержит ли код визуализацию"""
    viz_patterns = [
        r'import matplotlib',
        r'from matplotlib',
        r'plt\.(plot|scatter|bar|hist|figure|subplots)',
        r'import plotly',
        r'from plotly',
        r'px\.(line|scatter|bar)',
        r'go\.(Figure|Scatter)',
        r'import seaborn',
        r'sns\.(lineplot|scatterplot|histplot)',
        r'\.show\(\)'
    ]
    
    return any(re.search(pattern, code) for pattern in viz_patterns)

def is_plotly_code(code: str) -> bool:
    """Проверяет, используется ли plotly"""
    return 'plotly' in code or 'px.' in code or 'go.' in code

def execute_visualization(code: str, timeout: int = 30) -> Optional[dict]:
    """
    Безопасно выполняет код визуализации
    
    Returns:
        dict с ключами:
        - type: 'matplotlib' | 'plotly' | 'error'
        - figure: объект figure
        - error: сообщение об ошибке (если type='error')
    """
    # Подготавливаем окружение
    env = {
        'plt': plt,
        'pd': pd,
        'np': np,
        'px': px,
        'go': go,
        '__builtins__': __builtins__,
    }
    
    # Перехватываем stdout/stderr
    stdout_capture = io.StringIO()
    
    try:
        # Выполняем код
        with contextlib.redirect_stdout(stdout_capture):
            exec(code, env)
        
        # Определяем тип визуализации
        if is_plotly_code(code):
            # Ищем переменную fig в окружении
            fig = env.get('fig')
            if fig is None:
                # Пытаемся найти любую plotly figure
                for var_name, var_value in env.items():
                    if isinstance(var_value, go.Figure):
                        fig = var_value
                        break
            
            if fig:
                return {'type': 'plotly', 'figure': fig}
            else:
                return {'type': 'error', 'error': 'Plotly figure не найдена. Убедитесь, что код создает переменную `fig`'}
        else:
            # Matplotlib
            fig = plt.gcf()
            if fig.get_axes():  # Проверяем, есть ли оси
                return {'type': 'matplotlib', 'figure': fig}
            else:
                plt.close(fig)
                return {'type': 'error', 'error': 'Matplotlib figure пуста'}
    
    except Exception as e:
        return {'type': 'error', 'error': str(e)}
    
    finally:
        # Закрываем все figure, чтобы избежать утечек памяти
        plt.close('all')

def render_visualization(code_blocks: List[Dict]):
    """Рендерит кнопки для запуска визуализации"""
    viz_blocks = [
        block for block in code_blocks 
        if block['language'] in ['python', 'py'] and is_visualization_code(block['code'])
    ]
    
    if not viz_blocks:
        return
    
    st.markdown("---")
    st.markdown("**📊 Визуализация:**")
    
    for i, block in enumerate(viz_blocks):
        with st.expander(f"👁 Показать график {i+1}", expanded=False):
            # Показываем код
            st.code(block['code'], language='python')
            
            # Кнопка запуска
            if st.button(f"🚀 Запустить визуализацию {i+1}", key=f"viz_{i}"):
                with st.spinner("Выполняю код..."):
                    result = execute_visualization(block['code'])
                    
                    if result['type'] == 'matplotlib':
                        st.pyplot(result['figure'])
                    elif result['type'] == 'plotly':
                        st.plotly_chart(result['figure'], use_container_width=True)
                    elif result['type'] == 'error':
                        st.error(f"❌ Ошибка выполнения: {result['error']}")
