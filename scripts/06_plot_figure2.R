# Figure 2: statement-level coding of the 18 selected documents
#
# Script jobs
# 1- Load the coding outputs of 05_code_provisions.py
# 2- Panel A: share of statements carrying each conservation logic, per document (ordered by year)
# 3- Panel B: ES statements by function and operationality
# 4- Write the figure as a pgfplots picture and compile it with pdfLaTeX, so every
#    label is set in the article's own font (Latin Modern Roman, T1)
#
# Needs only base R and a LaTeX installation with pgfplots and standalone.
# Usage, from the repository root: Rscript scripts/06_plot_figure2.R [coding_folder] [output_folder]

args <- commandArgs(trailingOnly = TRUE)
coding_folder <- if (length(args) >= 1) args[1] else file.path("data", "legislation", "coding")
output_folder <- if (length(args) >= 2) args[2] else coding_folder

logic_file <- file.path(coding_folder, "logic_by_document.csv")
es_file <- file.path(coding_folder, "es_statements.csv")
figure_name <- "figure2"

# Colours (Okabe-Ito for the logics, one blue ramp for operationality) and labels

logic_styles <- data.frame(
  column = c("command_control_share", "market_valuation_share", "participatory_plural_share"),
  label = c("Command-and-control", "Market-valuation", "Participatory-plural"),
  colour = c("0072B2", "D55E00", "009E73"),
  marker = c("square*", "*", "triangle*"),
  size = c("2.2pt", "2.4pt", "2.9pt")
)

operationality_styles <- data.frame(
  value = c("declarative", "deferring", "operational"),
  label = c("Declarative", "Deferring", "Operational"),
  colour = c("A9CCEB", "4A90C8", "0B4A7E"),
  text = c("black!80", "white", "white")
)

function_labels <- c(
  market_valuation = "Market-valuation",
  general_es = "General ES",
  participatory_plural = "Participatory-plural",
  command_control = "Command-and-control"
)

periods <- data.frame(
  label = c("1996--2000", "2001--2007", "2008--2013", "2014--2022"),
  first = c(1996, 2001, 2008, 2014),
  last = c(2000, 2007, 2013, 2022)
)

# Data

logic <- read.csv(logic_file, fileEncoding = "UTF-8-BOM", stringsAsFactors = FALSE)
logic <- logic[order(logic$year, logic$label_en), ]
logic$row <- seq_len(nrow(logic))
logic$ylabel <- paste0(logic$label_en, " (", logic$year, ")")

es <- read.csv(es_file, fileEncoding = "UTF-8-BOM", stringsAsFactors = FALSE)
counts <- table(
  factor(es$es_function, levels = names(function_labels)),
  factor(es$operationality, levels = operationality_styles$value)
)
counts <- counts[rowSums(counts) > 0, , drop = FALSE]

# Helpers for writing pgfplots code

fmt <- function(x) sprintf("%.2f", x)
coords <- function(x, y) paste0("(", fmt(x), ",", y, ")", collapse = " ")

# Panel A

n_docs <- nrow(logic)
shares <- as.matrix(logic[, logic_styles$column]) * 100
x_max <- 10 * ceiling(max(shares) / 10)

panel_a <- c(
  r"(\begin{axis}[name=a, panel, height=10.6cm,)",
  sprintf("  xmin=0, xmax=%d, ymin=0.4, ymax=%.1f, y dir=reverse,", x_max, n_docs + 0.6),
  sprintf("  ytick={1,...,%d}, yticklabels={%s},", n_docs, paste0("{", logic$ylabel, "}", collapse = ",")),
  r"(  xlabel={Share of statements carrying each logic (\%)},)",
  r"(  legend to name=legendA, legend columns=3,)",
  r"(  legend style={draw=none, font=\footnotesize, /tikz/every even column/.append style={column sep=1.2em}},)",
  r"(])"
)

# Period bands: shade every other period and label each one on the right
for (i in seq_len(nrow(periods))) {
  rows <- logic$row[logic$year >= periods$first[i] & logic$year <= periods$last[i]]
  top <- min(rows) - 0.5
  bottom <- max(rows) + 0.5
  if (i %% 2 == 0) {
    panel_a <- c(panel_a, sprintf(
      r"(\fill[black!4] (axis cs:0,%.1f) rectangle (axis cs:%d,%.1f);)", top, x_max, bottom
    ))
  }
  panel_a <- c(panel_a, sprintf(
    r"(\node[period] at (axis cs:%d,%.1f) {%s};)", x_max, (top + bottom) / 2, periods$label[i]
  ))
}

# Range line linking the three logics of each document
for (i in seq_len(n_docs)) {
  panel_a <- c(panel_a, sprintf(
    r"(\addplot[black!22, line width=0.9pt, forget plot] coordinates {(%s,%d) (%s,%d)};)",
    fmt(min(shares[i, ])), i, fmt(max(shares[i, ])), i
  ))
}

for (j in seq_len(nrow(logic_styles))) {
  panel_a <- c(panel_a,
    sprintf(
      r"(\addplot[only marks, mark=%s, mark size=%s, color=c%d, mark options={draw=white, line width=0.35pt}] coordinates {%s};)",
      logic_styles$marker[j], logic_styles$size[j], j, coords(shares[, j], logic$row)
    ),
    sprintf(r"(\addlegendentry{%s})", logic_styles$label[j])
  )
}

panel_a <- c(panel_a,
  r"(\end{axis})",
  r"(\node[title, anchor=south west] at ([yshift=8pt]a.north -| a.outer west) {A.\enspace Conservation logics within each selected document};)",
  r"(\node[anchor=north] (la) at ([yshift=-2pt]a.outer south -| a.south) {\pgfplotslegendfromname{legendA}};)",
  r"(\node[title, anchor=north west] (tb) at ([yshift=-16pt]la.south -| a.outer west) {B.\enspace ES statements by function and operationality};)",
  r"(\coordinate (bpos) at ([yshift=-8pt]tb.south -| a.south west);)"
)

# Panel B

n_functions <- nrow(counts)
x_max_b <- 5 * ceiling(max(rowSums(counts)) / 5)

panel_b <- c(
  r"(\begin{axis}[name=b, panel, at={(bpos)}, anchor=north west, height=3.3cm,)",
  sprintf("  xbar stacked, bar width=9pt, xmin=0, xmax=%d, ymin=0.4, ymax=%.1f, y dir=reverse,", x_max_b, n_functions + 0.6),
  sprintf("  ytick={1,...,%d}, yticklabels={%s},", n_functions,
          paste0("{", function_labels[rownames(counts)], "}", collapse = ",")),
  r"(  xlabel={Number of ES statements},)",
  r"(  legend to name=legendB, legend columns=3, area legend,)",
  r"(  legend style={draw=none, font=\footnotesize, /tikz/every even column/.append style={column sep=1.2em}},)",
  r"(])"
)

for (j in seq_len(nrow(operationality_styles))) {
  panel_b <- c(panel_b,
    sprintf(r"(\addplot[fill=o%d, draw=white, line width=0.8pt] coordinates {%s};)",
            j, paste0("(", counts[, j], ",", seq_len(n_functions), ")", collapse = " ")),
    sprintf(r"(\addlegendentry{%s})", operationality_styles$label[j])
  )
}

# Counts printed in the middle of each segment wide enough to hold them,
# after the bars are drawn so they sit on top
ends <- t(apply(counts, 1, cumsum))
bar_labels <- character(0)
for (i in seq_len(n_functions)) {
  for (j in seq_len(nrow(operationality_styles))) {
    if (counts[i, j] >= 2) {
      bar_labels <- c(bar_labels, sprintf(
        r"(    \node[font=\scriptsize, text=%s] at (axis cs:%s,%d) {%d};)",
        operationality_styles$text[j], fmt(ends[i, j] - counts[i, j] / 2), i, counts[i, j]
      ))
    }
  }
}
options_end <- match(r"(])", panel_b)
panel_b <- append(panel_b, c(r"(  after end axis/.code={)", bar_labels, r"(  },)"), after = options_end - 1)

panel_b <- c(panel_b,
  r"(\end{axis})",
  r"(\node[anchor=north] at ([yshift=-2pt]b.outer south -| b.south) {\pgfplotslegendfromname{legendB}};)"
)

# Document

colour_defs <- c(
  sprintf(r"(\definecolor{c%d}{HTML}{%s})", seq_len(nrow(logic_styles)), logic_styles$colour),
  sprintf(r"(\definecolor{o%d}{HTML}{%s})", seq_len(nrow(operationality_styles)), operationality_styles$colour)
)

tex <- c(
  r"(% Generated by 06_plot_figure2.R -- do not edit by hand)",
  r"(\documentclass[12pt, border=1pt]{standalone})",
  r"(\usepackage[T1]{fontenc})",
  r"(\usepackage{lmodern})",
  r"(\usepackage{pgfplots})",
  r"(\pgfplotsset{compat=1.18})",
  colour_defs,
  r"(\pgfplotsset{panel/.style={)",
  r"(  width=9.2cm, scale only axis, font=\footnotesize, set layers,)",
  r"(  axis line style={black!55, line width=0.4pt}, axis x line*=bottom, axis y line*=left,)",
  r"(  tick style={black!55, line width=0.4pt}, major tick length=2.5pt,)",
  r"(  y tick style={draw=none}, yticklabel style={font=\footnotesize, text=black!85},)",
  r"(  xticklabel style={font=\footnotesize, text=black!85}, xlabel style={font=\footnotesize, text=black!85},)",
  r"(  xmajorgrids, major grid style={black!12, line width=0.4pt},)",
  r"(  clip=false, axis on top=false, enlargelimits=false,)",
  r"(}})",
  r"(\tikzset{title/.style={font=\small\bfseries, inner sep=0pt},)",
  r"(  period/.style={font=\scriptsize\itshape, text=black!60, anchor=west, xshift=4pt}})",
  r"(\begin{document})",
  r"(\begin{tikzpicture})",
  panel_a,
  panel_b,
  r"(\end{tikzpicture})",
  r"(\end{document})"
)


dir.create(output_folder, showWarnings = FALSE, recursive = TRUE)
tex_file <- file.path(output_folder, paste0(figure_name, ".tex"))
writeLines(tex, tex_file, useBytes = TRUE)

# Compile

old_wd <- setwd(output_folder)
status <- system2("pdflatex", c("-interaction=nonstopmode", "-halt-on-error", paste0(figure_name, ".tex")),
                  stdout = FALSE, stderr = FALSE)
setwd(old_wd)
if (status != 0) stop("pdfLaTeX failed; see ", file.path(output_folder, paste0(figure_name, ".log")))
for (ext in c(".aux", ".log")) unlink(file.path(output_folder, paste0(figure_name, ext)))

cat("Saved to:", file.path(output_folder, paste0(figure_name, ".pdf")), "\n")
