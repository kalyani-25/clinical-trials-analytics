# Project 5: Meta-Analysis in R with Forest Plots
# Install packages: install.packages(c("meta", "metafor", "ggplot2", "dplyr", "readr"))
# Run: Rscript meta_analysis.R

library(dplyr)

set.seed(42)
n_studies <- 12

studies <- data.frame(
  study     = paste0("Study ", LETTERS[1:n_studies]),
  year      = sample(2015:2023, n_studies, replace = TRUE),
  area      = sample(c("Oncology","Cardiology","Neurology"), n_studies, replace = TRUE),
  n_treated = sample(50:500, n_studies),
  n_control = sample(50:500, n_studies),
  or        = round(exp(rnorm(n_studies, mean = 0.4, sd = 0.3)), 2)
)
studies$se        <- round(abs(rnorm(n_studies, 0.15, 0.05)), 3)
studies$lower_ci  <- round(studies$or * exp(-1.96 * studies$se), 2)
studies$upper_ci  <- round(studies$or * exp( 1.96 * studies$se), 2)
studies$log_or    <- log(studies$or)

cat("=== Study Data for Forest Plot ===\n")
print(studies[, c("study","year","area","or","lower_ci","upper_ci","n_treated","n_control")])

# Fixed-effects pooled OR
weights   <- 1 / studies$se^2
pooled_or <- exp(sum(weights * studies$log_or) / sum(weights))
pooled_se <- sqrt(1 / sum(weights))
cat(sprintf("\nFixed-effects pooled OR: %.3f (95%% CI: %.3f - %.3f)\n",
            pooled_or,
            exp(log(pooled_or) - 1.96 * pooled_se),
            exp(log(pooled_or) + 1.96 * pooled_se)))

write.csv(studies, "meta_analysis_data.csv", row.names = FALSE)
cat("Saved meta_analysis_data.csv\n")

# Forest plot with meta package
if (requireNamespace("meta", quietly = TRUE)) {
  library(meta)
  m <- metagen(
    TE     = log_or,
    seTE   = se,
    data   = studies,
    sm     = "OR",
    studlab = study,
    title  = "Clinical Trial Outcomes Meta-Analysis"
  )
  png("forest_plot.png", width = 900, height = 600, res = 100)
  forest(m,
         sortvar    = or,
         print.tau2 = TRUE,
         col.diamond = "steelblue",
         col.square  = "#378ADD",
         xlab       = "Odds Ratio (log scale)")
  dev.off()
  cat("Saved forest_plot.png\n")
} else {
  cat("\nInstall meta package for forest plot:\n")
  cat("  install.packages('meta')\n")
  cat("  Then: forest(metagen(log_or, se, data=studies, sm='OR', studlab=study))\n")
}
