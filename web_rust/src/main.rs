use axum::body::Body;
use axum::extract::{Path, Query};
use axum::response::IntoResponse;
use axum::{response::Json, routing::get, Router};
use serde::Deserialize;
use tower_http::cors::{Any, CorsLayer};
use tower_http::services::ServeDir;
use tower_http::trace::TraceLayer;

mod data;

#[derive(Deserialize)]
struct SearchParams {
    keyword: String,
}

async fn health_check() -> &'static str {
    "OK"
}

async fn list_brands() -> Json<Vec<data::BrandGroup>> {
    let base_url =
        std::env::var("BASE_URL").unwrap_or_else(|_| "http://localhost:3000".to_string());
    Json(data::get_brands(&base_url))
}

async fn list_models(Path(brand_id): Path<String>) -> Json<Vec<data::Model>> {
    Json(data::get_models(&brand_id))
}

async fn search_brands(Query(params): Query<SearchParams>) -> Json<Vec<data::Brand>> {
    let base_url =
        std::env::var("BASE_URL").unwrap_or_else(|_| "http://localhost:3000".to_string());
    Json(data::search_brands(&base_url, &params.keyword))
}

async fn search_files(Query(params): Query<SearchParams>) -> Json<Vec<String>> {
    Json(data::search_files(&params.keyword))
}

#[derive(Deserialize)]
struct BrandQuery {
    brand: String,
}

async fn list_brand_files(Query(params): Query<BrandQuery>) -> Json<Vec<data::FolderFiles>> {
    Json(data::get_brand_files(&params.brand))
}

#[derive(Deserialize)]
struct PdfQuery {
    brand: String,
    path: String,
}

async fn view_pdf(Query(params): Query<PdfQuery>) -> impl IntoResponse {
    let base = std::path::Path::new("car_pdfs")
        .canonicalize()
        .unwrap_or_else(|_| std::env::current_dir().unwrap_or_default().join("car_pdfs"));
    let target = base.join(&params.brand).join(&params.path);

    let canonical = match target.canonicalize() {
        Ok(p) => p,
        Err(_) => return axum::http::StatusCode::NOT_FOUND.into_response(),
    };

    if !canonical.starts_with(&base) || !canonical.is_file() {
        return axum::http::StatusCode::FORBIDDEN.into_response();
    }

    let content = match tokio::fs::read(&canonical).await {
        Ok(c) => c,
        Err(_) => return axum::http::StatusCode::INTERNAL_SERVER_ERROR.into_response(),
    };

    axum::http::Response::builder()
        .status(axum::http::StatusCode::OK)
        .header(axum::http::header::CONTENT_TYPE, "application/pdf")
        .body(Body::from(content))
        .unwrap()
}

#[tokio::main]
async fn main() {
    tracing_subscriber::fmt()
        .with_env_filter("car_instr_api=debug,tower_http=debug")
        .init();

    let cors = CorsLayer::new()
        .allow_origin(Any)
        .allow_methods(Any)
        .allow_headers(Any);

    let app = Router::new()
        .route("/health", get(health_check))
        .route("/api/brands", get(list_brands))
        .route("/api/brands/search", get(search_brands))
        .route("/api/files/search", get(search_files))
        .route("/api/files/list", get(list_brand_files))
        .route("/api/files/view", get(view_pdf))
        .route("/api/brands/{id}/models", get(list_models))
        .nest_service("/static", ServeDir::new("static"))
        .layer(cors)
        .layer(TraceLayer::new_for_http());

    let listener = tokio::net::TcpListener::bind("0.0.0.0:3000").await.unwrap();
    tracing::info!("Server running on http://172.16.22.14:3000");

    axum::serve(listener, app).await.unwrap();
}
