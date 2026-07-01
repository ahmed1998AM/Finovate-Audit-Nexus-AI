import plotly.graph_objects as go
from plotly.offline import plot
from typing import List, Dict, Any, Optional
from pathlib import Path

from frontend.styles.design_system import Color


FINOVATE_COLORS = {
    "primary": Color.PRIMARY,
    "secondary": Color.PRIMARY_HOVER,
    "success": Color.SUCCESS,
    "warning": Color.WARNING,
    "error": Color.ERROR,
    "info": Color.INFO,
    "text": Color.TEXT_WHITE,
    "text_muted": Color.TEXT_SECONDARY,
    "border": Color.BORDER,
    "bg": Color.BG_DARK,
    "surface": Color.BG_MEDIUM,
    "card": Color.BG_CARD,
}


class FinancialChart:
    PALETTE = [
        Color.PRIMARY, Color.SUCCESS, Color.WARNING,
        Color.ERROR, Color.INFO, Color.PRIMARY_HOVER,
    ]

    def __init__(self, theme: str = "dark"):
        self.theme = theme
        self.template = "plotly_dark" if theme == "dark" else "plotly_white"
        self.colors = FINOVATE_COLORS

    def create_trend_chart(self, data: List[Dict], title: str = "Financial Trend",
                           x_key: str = "period", y_keys: List[str] = None,
                           output_path: str = None) -> str:
        fig = go.Figure()
        if not y_keys:
            y_keys = [key for key in data[0].keys() if key != x_key]
        for i, y_key in enumerate(y_keys):
            fig.add_trace(go.Scatter(
                x=[item[x_key] for item in data],
                y=[item[y_key] for item in data],
                mode='lines+markers',
                name=y_key.replace('_', ' ').title(),
                line=dict(width=2.5, color=self.PALETTE[i % len(self.PALETTE)]),
                marker=dict(size=7, color=self.PALETTE[i % len(self.PALETTE)])
            ))
        fig.update_layout(
            title=dict(text=title, font=dict(size=18, family="Segoe UI", color=self.colors["text"])),
            xaxis=dict(gridcolor=self.colors["border"], color=self.colors["text_muted"]),
            yaxis=dict(gridcolor=self.colors["border"], color=self.colors["text_muted"]),
            template=self.template,
            hovermode='x unified',
            legend=dict(orientation="h", y=1.02, xanchor="right", x=1,
                       font=dict(color=self.colors["text_muted"])),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)'
        )
        if output_path:
            plot(fig, filename=output_path, auto_open=False)
            return output_path
        return fig.to_html(include_plotlyjs='cdn')

    def create_bar_chart(self, categories: List[str], values: List[float],
                         title: str = "Financial Analysis",
                         color: str = None, output_path: str = None) -> str:
        if not color:
            color = self.colors["primary"]
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=categories, y=values,
            marker_color=color,
            marker_line=dict(width=1, color=self.colors["border"]),
            text=[f"{v:,.2f}" for v in values],
            textposition='auto',
            textfont=dict(color=self.colors["text"]),
            hovertemplate='<b>%{x}</b><br>Value: %{y:,.2f}<extra></extra>'
        ))
        fig.update_layout(
            title=dict(text=title, font=dict(size=18, family="Segoe UI", color=self.colors["text"])),
            xaxis=dict(gridcolor=self.colors["border"], color=self.colors["text_muted"]),
            yaxis=dict(gridcolor=self.colors["border"], color=self.colors["text_muted"]),
            template=self.template,
            showlegend=False,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)'
        )
        if output_path:
            plot(fig, filename=output_path, auto_open=False)
            return output_path
        return fig.to_html(include_plotlyjs='cdn')

    def create_pie_chart(self, labels: List[str], values: List[float],
                         title: str = "Distribution", output_path: str = None) -> str:
        colors = self.PALETTE[:len(labels)]
        fig = go.Figure(data=[go.Pie(
            labels=labels, values=values, hole=0.4,
            marker_colors=colors,
            textinfo='percent+label',
            textfont=dict(color=self.colors["text"], size=12),
            hovertemplate='<b>%{label}</b><br>Value: %{value:,.2f}<br>Percentage: %{percent}<extra></extra>'
        )])
        fig.update_layout(
            title=dict(text=title, font=dict(size=18, family="Segoe UI", color=self.colors["text"])),
            template=self.template,
            showlegend=True,
            legend=dict(font=dict(color=self.colors["text_muted"]), x=1, y=0.5),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)'
        )
        if output_path:
            plot(fig, filename=output_path, auto_open=False)
            return output_path
        return fig.to_html(include_plotlyjs='cdn')

    def create_heatmap(self, data: List[List[float]], x_labels: List[str],
                       y_labels: List[str], title: str = "Risk Heatmap",
                       output_path: str = None) -> str:
        fig = go.Figure(data=go.Heatmap(
            z=data, x=x_labels, y=y_labels,
            colorscale='RdYlGn_r',
            hovertemplate='%{x} vs %{y}<br>Risk: %{z:.2f}<extra></extra>',
            colorbar=dict(title="Risk Level", tickfont=dict(color=self.colors["text"]),
                         titlefont=dict(color=self.colors["text_muted"]))
        ))
        fig.update_layout(
            title=dict(text=title, font=dict(size=18, family="Segoe UI", color=self.colors["text"])),
            xaxis=dict(gridcolor=self.colors["border"], color=self.colors["text_muted"]),
            yaxis=dict(gridcolor=self.colors["border"], color=self.colors["text_muted"]),
            template=self.template,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)'
        )
        if output_path:
            plot(fig, filename=output_path, auto_open=False)
            return output_path
        return fig.to_html(include_plotlyjs='cdn')

    def create_waterfall_chart(self, labels: List[str], values: List[float],
                                title: str = "Waterfall Analysis",
                                output_path: str = None) -> str:
        measures = []
        for i, value in enumerate(values):
            if i == 0 or i == len(values) - 1:
                measures.append("absolute")
            elif value >= 0:
                measures.append("relative")
            else:
                measures.append("relative")
        fig = go.Figure(go.Waterfall(
            name="Financial Waterfall", orientation="v",
            measure=measures, x=labels,
            textposition="outside",
            text=[f"{v:,.2f}" for v in values],
            textfont=dict(color=self.colors["text"], size=11),
            y=values,
            connector=dict(line=dict(color=self.colors["border"], width=1.5)),
            increasing={"marker": {"color": self.colors["success"]}},
            decreasing={"marker": {"color": self.colors["error"]}},
            totals={"marker": {"color": self.colors["primary"]}}
        ))
        fig.update_layout(
            title=dict(text=title, font=dict(size=18, family="Segoe UI", color=self.colors["text"])),
            showlegend=False, template=self.template,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)'
        )
        if output_path:
            plot(fig, filename=output_path, auto_open=False)
            return output_path
        return fig.to_html(include_plotlyjs='cdn')

    def create_kpi_cards_data(self, kpis: Dict[str, Any]) -> List[Dict]:
        cards = []
        for name, value in kpis.items():
            status = "normal"
            if isinstance(value, (int, float)):
                if value > 0:
                    status = "success"
                elif value < 0:
                    status = "error"
            cards.append({
                "title": name.replace('_', ' ').title(),
                "value": f"{value:,.2f}" if isinstance(value, (int, float)) else str(value),
                "status": status
            })
        return cards
