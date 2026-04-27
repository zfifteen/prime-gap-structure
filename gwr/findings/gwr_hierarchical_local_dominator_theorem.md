```latex
\begin{theorem}[Gap Winner Rule — Hierarchical Local-Dominator Law]
Let \(p < q\) be any two consecutive primes with composite interior
\[
I = \{p+1, \dots, q-1\}.
\]
Define the minimal divisor class present in the gap by
\[
\delta_{\min}(p,q) := \min_{n \in I} d(n)
\]
and let
\[
w := \min\{ n \in I : d(n) = \delta_{\min}(p,q) \}
\]
be the leftmost integer of that class.

Then the following three properties hold simultaneously:

\begin{enumerate}
\item \textbf{Hierarchical First-Arrival:} 
\(w\) is the leftmost integer in \(I\) attaining the global minimal divisor count present in the gap.

\item \textbf{Local-Dominator Property (Left Flank):} 
For every earlier composite \(a \in I\) with \(a < w\), there exists at least one admissible composite \(b \in I\) such that
\[
a < b < q \quad \text{and} \quad L(b) > L(a),
\]
where
\[
L(n) = \left(1 - \frac{d(n)}{2}\right) \ln n
\]
is the raw-\(Z\) log-score.

\item \textbf{No-Later-Simpler-Composite Property (Right Flank):} 
There exists no \(m \in I\) with \(m > w\) and \(d(m) < d(w)\).
\end{enumerate}

Consequently, \(w\) is the unique maximizer of the raw-\(Z\) (equivalently log-score) function over the entire gap interior \(I\).
\end{theorem}
```
