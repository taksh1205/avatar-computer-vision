# OSU avatar-feature models
# Requested pooled specification: wd_flag * feature + version_enc + controls.
# Uses base R only. HC1 covariance is calculated explicitly.

main <- read.csv(
  "d_osu_final.csv",
  check.names = FALSE,
  stringsAsFactors = FALSE,
  na.strings = c("", "NA")
)
features <- read.csv(
  "OSU_avatar_features_final.csv",
  check.names = FALSE,
  stringsAsFactors = FALSE,
  na.strings = c("", "NA")
)

merge_ids <- c("Version.ID", "User.ID")
if (!all(merge_ids %in% names(main))) {
  stop("Main file must contain Version.ID and User.ID.")
}
if (!all(merge_ids %in% names(features))) {
  stop("Feature file must contain Version.ID and User.ID.")
}

duplicates <- intersect(
  setdiff(names(main), merge_ids),
  setdiff(names(features), merge_ids)
)
if (length(duplicates) > 0) {
  stop(
    paste(
      "Duplicate non-ID columns:",
      paste(duplicates, collapse = ", ")
    )
  )
}

dat <- merge(
  main,
  features,
  by = merge_ids,
  all = FALSE,
  sort = FALSE
)
if (nrow(dat) != 190) {
  stop(paste("Expected 190 merged rows; found", nrow(dat)))
}

dat$version_enc <- factor(
  dat$version_enc,
  levels = c("create_av", "human_av", "no_av")
)
dat$wd_flag <- as.numeric(as.character(dat$wd_flag))

# Enforce the professor-requested availability rule after merging. Some legacy
# final_* columns already exist in the main file, so they are explicitly set to
# missing outside create_av before any model is run.
non_create <- is.na(dat$version_enc) | dat$version_enc != "create_av"
final_columns <- grep("^final_", names(dat), value = TRUE)
if (length(final_columns) > 0) {
  for (column in final_columns) {
    dat[non_create, column] <- NA
  }
  final_nonmissing <- vapply(
    dat[non_create, final_columns, drop = FALSE],
    function(x) sum(!is.na(x)),
    numeric(1)
  )
  if (any(final_nonmissing > 0)) {
    stop("At least one final_* feature is populated outside create_av.")
  }
}

controls <- c(
  "robot_comfort",
  "age",
  "gender",
  "racewhite",
  "educ",
  "subj_stress1"
)

pooled_numeric <- c(
  "first_avatar_gender_match",
  "first_logo_binary",
  "first_avatar_happy_binary",
  "first_avatar_formal_binary",
  "first_mean_saturation_0_255",
  "first_mean_brightness_0_255",
  "first_color_arousal_binary_high",
  "first_color_valence_binary_positive",
  "first_warm_color_binary",
  "first_neutral_color_binary",
  "first_realism_proxy_0_100",
  "first_craftsmanship_complexity_proxy_0_100",
  "first_human_likeness_proxy_0_100",
  "first_roboticness_proxy_0_100",
  "first_dimension_3d_binary",
  "first_rendering_style_tier_0_3",
  "first_perceived_age_older_binary",
  "first_facial_feature_count_proxy_0_4",
  "first_visible_mechanical_complexity_0_3",
  "first_attire_completeness_0_2",
  "first_tie_bow_tie_proxy",
  "first_color_coordination_score_1_5",
  "first_aesthetic_coherence_score_1_7",
  "first_role_congruence_score_1_5",
  "first_warmth_approachability_score_1_7",
  "first_cartoonish_binary",
  "first_realistic_binary",
  "first_craftsmanship_weighted_0_100",
  "first_eyelashes_present_visual_proxy",
  "first_visible_iris_present_visual_proxy",
  "first_skin_shading_present_visual_proxy",
  "first_blush_present_visual_proxy",
  "first_eyebrows_present_visual_proxy",
  "first_visible_teeth_present_visual_proxy",
  "first_mechanical_neck_present_visual_proxy",
  "first_panel_seams_present_visual_proxy",
  "first_name_badge_present_visual_proxy",
  "first_tie_bow_tie_present_filename_rule",
  "first_logo_present_filename_rule",
  "first_feature_inventory_count_0_12",
  "first_saturation_high_binary",
  "first_brightness_high_binary",
  "avatar_female_binary",
  "avatar_happy_binary",
  "avatar_formal_binary",
  "realism_proxy_0_100",
  "craftsmanship_complexity_proxy_0_100",
  "realism_proxy_z",
  "craftsmanship_proxy_z",
  "first_aesthetic_coherence_score_1_7_z",
  "first_color_coordination_score_1_5_z",
  "first_craftsmanship_complexity_proxy_0_100_z",
  "first_craftsmanship_weighted_0_100_z",
  "first_feature_inventory_count_0_12_z",
  "first_human_likeness_proxy_0_100_z",
  "first_realism_proxy_0_100_z",
  "first_role_congruence_score_1_5_z",
  "first_warmth_approachability_score_1_7_z"
)
pooled_categorical <- c(
  "first_avatar_gender",
  "first_avatar_emotion",
  "first_clothing_color",
  "first_attire_style",
  "first_logo_presence",
  "first_image_variant",
  "first_saturation_level",
  "first_brightness_level",
  "first_color_arousal_level",
  "first_color_valence_level",
  "first_color_temperature",
  "first_human_likeness_level",
  "first_roboticness_level",
  "first_dimension_style_proxy",
  "first_rendering_style_label",
  "first_perceived_age_group",
  "first_realism_style",
  "first_craftsmanship_quality_level",
  "first_apparent_role_confidence",
  "realism_style",
  "craftsmanship_level"
)
final_numeric <- c(
  "final_avatar_gender_match",
  "final_logo_binary",
  "final_avatar_happy_binary",
  "final_avatar_formal_binary",
  "final_mean_saturation_0_255",
  "final_mean_brightness_0_255",
  "final_color_arousal_binary_high",
  "final_color_valence_binary_positive",
  "final_warm_color_binary",
  "final_neutral_color_binary",
  "final_realism_proxy_0_100",
  "final_craftsmanship_complexity_proxy_0_100",
  "final_human_likeness_proxy_0_100",
  "final_roboticness_proxy_0_100",
  "final_dimension_3d_binary",
  "final_rendering_style_tier_0_3",
  "final_perceived_age_older_binary",
  "final_facial_feature_count_proxy_0_4",
  "final_visible_mechanical_complexity_0_3",
  "final_attire_completeness_0_2",
  "final_tie_bow_tie_proxy",
  "final_color_coordination_score_1_5",
  "final_aesthetic_coherence_score_1_7",
  "final_role_congruence_score_1_5",
  "final_warmth_approachability_score_1_7",
  "final_cartoonish_binary",
  "final_realistic_binary",
  "final_craftsmanship_weighted_0_100",
  "final_eyelashes_present_visual_proxy",
  "final_visible_iris_present_visual_proxy",
  "final_skin_shading_present_visual_proxy",
  "final_blush_present_visual_proxy",
  "final_eyebrows_present_visual_proxy",
  "final_visible_teeth_present_visual_proxy",
  "final_mechanical_neck_present_visual_proxy",
  "final_panel_seams_present_visual_proxy",
  "final_name_badge_present_visual_proxy",
  "final_tie_bow_tie_present_filename_rule",
  "final_logo_present_filename_rule",
  "final_feature_inventory_count_0_12",
  "distinct_avatars_created_v1",
  "any_avatar_gender_match",
  "final_saturation_high_binary",
  "final_brightness_high_binary",
  "final_avatar_logo_binary",
  "final_aesthetic_coherence_score_1_7_z",
  "final_color_coordination_score_1_5_z",
  "final_craftsmanship_complexity_proxy_0_100_z",
  "final_craftsmanship_weighted_0_100_z",
  "final_feature_inventory_count_0_12_z",
  "final_human_likeness_proxy_0_100_z",
  "final_realism_proxy_0_100_z",
  "final_role_congruence_score_1_5_z",
  "final_warmth_approachability_score_1_7_z"
)
final_categorical <- c(
  "final_avatar_gender",
  "final_avatar_emotion",
  "final_clothing_color",
  "final_attire_style",
  "final_logo_presence",
  "final_image_variant",
  "final_saturation_level",
  "final_brightness_level",
  "final_color_arousal_level",
  "final_color_valence_level",
  "final_color_temperature",
  "final_human_likeness_level",
  "final_roboticness_level",
  "final_dimension_style_proxy",
  "final_rendering_style_label",
  "final_perceived_age_group",
  "final_realism_style",
  "final_craftsmanship_quality_level",
  "final_apparent_role_confidence",
  "interaction_intensity_v1",
  "final_avatar_color",
  "final_avatar_attire",
  "final_avatar_variant"
)

# Verify that every pooled feature has nonmissing observations in both avatar
# conditions. IDs 8 and 148 remain documented image-unavailable exceptions.
pooled_features <- unique(c(pooled_numeric, pooled_categorical))
for (feature in pooled_features) {
  if (!feature %in% names(dat)) {
    stop(paste("Missing pooled feature:", feature))
  }
  create_count <- sum(
    dat$version_enc == "create_av" & !is.na(dat[[feature]])
  )
  human_count <- sum(
    dat$version_enc == "human_av" & !is.na(dat[[feature]])
  )
  if (create_count == 0 || human_count == 0) {
    stop(
      paste(
        "Pooled feature lacks coverage in one avatar condition:",
        feature,
        "create_av =", create_count,
        "human_av =", human_count
      )
    )
  }
}

quote_name <- function(x) {
  paste0("`", gsub("`", "", x), "`")
}

extract_robust <- function(model, model_id, scope, feature, feature_type) {
  design <- stats::model.matrix(model)
  residual_vector <- stats::residuals(model)
  n <- nrow(design)
  k <- ncol(design)

  if (qr(design)$rank < k) {
    stop("Cannot calculate HC1 covariance for a rank-deficient model.")
  }

  bread <- solve(crossprod(design))
  meat <- crossprod(
    design,
    design * as.numeric(residual_vector)^2
  )
  robust_vcov <- (n / (n - k)) * bread %*% meat %*% bread
  robust_se <- sqrt(diag(robust_vcov))
  estimates <- stats::coef(model)
  t_value <- estimates / robust_se
  degrees_freedom <- n - k
  p_value <- 2 * stats::pt(
    abs(t_value),
    df = degrees_freedom,
    lower.tail = FALSE
  )
  critical_value <- stats::qt(0.975, df = degrees_freedom)

  data.frame(
    model_id = model_id,
    scope = scope,
    feature = feature,
    feature_type = feature_type,
    formula = paste(deparse(stats::formula(model)), collapse = ""),
    n = stats::nobs(model),
    term = names(estimates),
    estimate = as.numeric(estimates),
    robust_se_HC1 = as.numeric(robust_se),
    p_value = as.numeric(p_value),
    ci_low_95 = as.numeric(estimates - critical_value * robust_se),
    ci_high_95 = as.numeric(estimates + critical_value * robust_se),
    r_squared = summary(model)$r.squared,
    adjusted_r_squared = summary(model)$adj.r.squared,
    row.names = NULL,
    check.names = FALSE
  )
}

fit_one <- function(feature, scope, feature_type) {
  if (!feature %in% names(dat)) {
    message("Skipping missing feature: ", feature)
    return(NULL)
  }

  if (scope == "pooled") {
    d <- dat[
      dat$version_enc %in% c("create_av", "human_av"),
      ,
      drop = FALSE
    ]
    d$version_enc <- droplevels(d$version_enc)
  } else {
    d <- dat[
      dat$version_enc == "create_av",
      ,
      drop = FALSE
    ]
  }

  required <- c("serv_qual", "wd_flag", feature, controls)
  if (scope == "pooled") required <- c(required, "version_enc")
  d <- d[stats::complete.cases(d[, required, drop = FALSE]), , drop = FALSE]

  if (nrow(d) < 25) {
    message("Skipping ", feature, ": fewer than 25 complete rows.")
    return(NULL)
  }

  if (feature_type == "categorical") {
    d[[feature]] <- factor(d[[feature]])
    if (nlevels(d[[feature]]) < 2 || nlevels(d[[feature]]) > 8) {
      message("Skipping ", feature, ": unsupported level count.")
      return(NULL)
    }
    feature_term <- paste0("factor(", quote_name(feature), ")")
  } else {
    d[[feature]] <- as.numeric(d[[feature]])
    if (length(unique(d[[feature]])) < 2) {
      message("Skipping ", feature, ": constant feature.")
      return(NULL)
    }
    feature_term <- quote_name(feature)
  }

  control_terms <- paste(
    vapply(controls, quote_name, character(1)),
    collapse = " + "
  )

  if (scope == "pooled") {
    formula_text <- paste0(
      "serv_qual ~ wd_flag * ",
      feature_term,
      " + version_enc + ",
      control_terms
    )
  } else {
    # final_* and V1-only features exist in create_av only. version_enc is
    # constant in that subset and is therefore not estimable.
    formula_text <- paste0(
      "serv_qual ~ wd_flag * ",
      feature_term,
      " + ",
      control_terms
    )
  }

  model <- stats::lm(
    stats::as.formula(formula_text),
    data = d
  )

  if (model$rank < ncol(stats::model.matrix(model))) {
    message("Skipping ", feature, ": rank-deficient model.")
    return(NULL)
  }

  extract_robust(
    model,
    paste(scope, feature, sep = "__"),
    ifelse(
      scope == "pooled",
      "create_av + human_av",
      "create_av only"
    ),
    feature,
    feature_type
  )
}

results <- list()

for (feature in pooled_numeric) {
  value <- fit_one(feature, "pooled", "numeric")
  if (!is.null(value)) results[[length(results) + 1]] <- value
}
for (feature in pooled_categorical) {
  value <- fit_one(feature, "pooled", "categorical")
  if (!is.null(value)) results[[length(results) + 1]] <- value
}
for (feature in final_numeric) {
  value <- fit_one(feature, "create_only", "numeric")
  if (!is.null(value)) results[[length(results) + 1]] <- value
}
for (feature in final_categorical) {
  value <- fit_one(feature, "create_only", "categorical")
  if (!is.null(value)) results[[length(results) + 1]] <- value
}

if (length(results) == 0) {
  stop("No models were successfully estimated.")
}

coefficients <- do.call(rbind, results)
write.csv(
  coefficients,
  "OSU_avatar_model_coefficients.csv",
  row.names = FALSE,
  na = ""
)

cat("Merged rows:", nrow(dat), "\n")
cat("Successful models:", length(unique(coefficients$model_id)), "\n")
cat("Coefficient rows:", nrow(coefficients), "\n")
cat("Saved: OSU_avatar_model_coefficients.csv\n")
