use pinyin::ToPinyin;
use serde::{Deserialize, Serialize};
use std::collections::{HashMap, HashSet};
use std::sync::OnceLock;

#[derive(Debug, Clone, Serialize)]
pub struct Brand {
    pub id: String,
    pub name: String,
    pub logo: String,
}

#[derive(Debug, Clone, Serialize)]
pub struct BrandGroup {
    pub letter: String,
    pub brands: Vec<Brand>,
}

#[derive(Debug, Clone, Serialize)]
pub struct Model {
    pub id: String,
    pub name: String,
    pub image: String,
    pub pdf: String,
    pub url: String,
}

#[derive(Debug, Deserialize)]
struct RawChild {
    name: String,
    dir_name: String,
    url: String,
    pdfs: Vec<String>,
}

#[derive(Debug, Deserialize)]
struct RawItem {
    parten: String,
    chrild: Vec<RawChild>,
}

static GROUPS: OnceLock<Vec<BrandGroup>> = OnceLock::new();
static MODELS: OnceLock<HashMap<String, Vec<Model>>> = OnceLock::new();

/// 获取字符串首字符的拼音首字母（大写）
fn get_pinyin_initial(s: &str) -> char {
    let first = s.chars().next().unwrap_or('?');
    if first.is_ascii_alphabetic() {
        return first.to_ascii_uppercase();
    }
    first
        .to_pinyin()
        .and_then(|p| p.first_letter().chars().next())
        .unwrap_or(first)
        .to_ascii_uppercase()
}

fn load() -> (Vec<BrandGroup>, HashMap<String, Vec<Model>>) {
    let path = std::path::Path::new("car_pdfs.json");
    let content = std::fs::read_to_string(path).unwrap_or_else(|_| "[]".to_string());
    let raw: Vec<RawItem> = serde_json::from_str(&content).unwrap_or_default();

    let mut letter_map: HashMap<char, Vec<Brand>> = HashMap::new();
    let mut models_map = HashMap::new();

    for item in raw {
        for child in item.chrild {
            let initial = get_pinyin_initial(&child.name);

            letter_map.entry(initial).or_default().push(Brand {
                id: child.dir_name.clone(),
                name: child.name.clone(),
                logo: String::new(),
            });

            let models: Vec<Model> = child
                .pdfs
                .into_iter()
                .map(|pdf| Model {
                    id: pdf.clone(),
                    name: pdf.replace(".pdf", ""),
                    image: String::new(),
                    pdf,
                    url: child.url.clone(),
                })
                .collect();

            models_map.insert(child.dir_name, models);
        }
    }

    // 按拼音首字母排序分组
    let mut initials: Vec<char> = letter_map.keys().cloned().collect();
    initials.sort();

    let groups = initials
        .into_iter()
        .map(|letter| {
            let mut brands = letter_map.remove(&letter).unwrap_or_default();
            brands.sort_by(|a, b| a.name.cmp(&b.name));
            BrandGroup {
                letter: letter.to_string(),
                brands,
            }
        })
        .collect();

    (groups, models_map)
}

fn ensure_loaded() {
    if GROUPS.get().is_none() {
        let (groups, models) = load();
        let _ = GROUPS.set(groups);
        let _ = MODELS.set(models);
    }
}

pub fn get_brands(_base_url: &str) -> Vec<BrandGroup> {
    ensure_loaded();
    GROUPS.get().cloned().unwrap_or_default()
}

pub fn get_models(brand_id: &str) -> Vec<Model> {
    ensure_loaded();
    MODELS
        .get()
        .and_then(|m| m.get(brand_id).cloned())
        .unwrap_or_default()
}

pub fn search_brands(_base_url: &str, keyword: &str) -> Vec<Brand> {
    let kw = keyword.trim().to_lowercase();
    if kw.is_empty() {
        return vec![];
    }
    let mut result = Vec::new();
    let mut seen = HashSet::new();
    if let Some(groups) = GROUPS.get() {
        for group in groups {
            for brand in &group.brands {
                if !seen.contains(&brand.id) && brand.name.to_lowercase().contains(&kw) {
                    seen.insert(brand.id.clone());
                    result.push(brand.clone());
                }
            }
        }
    }
    result
}

/// 一级目录名到中文品牌名的映射（用于支持按中文品牌名搜索）
fn brand_aliases() -> HashMap<&'static str, Vec<&'static str>> {
    let mut map = HashMap::new();
    map.insert("toyota", vec!["丰田", "广汽丰田"]);
    map.insert("byd", vec!["比亚迪", "byd"]);
    map.insert("dazhong", vec!["大众", "上汽大众"]);
    map.insert("beijing_yueye", vec!["北京越野", "北京"]);
    map.insert("changcheng_xi", vec!["长城", "哈弗", "坦克", "长城炮", "魏派", "欧拉", "wey"]);
    map.insert("dongfeng_fengxing", vec!["东风", "风行", "东风风行"]);
    map.insert("guangqi_chuanqi", vec!["传祺", "广汽", "广汽传祺"]);
    map
}

fn brand_name_matches(dir_name: &str, kw: &str) -> bool {
    let kw_lower = kw.to_lowercase();
    if dir_name.to_lowercase().contains(&kw_lower) {
        return true;
    }
    let aliases = brand_aliases();
    if let Some(names) = aliases.get(dir_name) {
        return names.iter().any(|n| n.to_lowercase().contains(&kw_lower));
    }
    false
}

/// 搜索只匹配一级目录品牌名，返回匹配的品牌目录名列表
pub fn search_files(keyword: &str) -> Vec<String> {
    let kw = keyword.trim().to_lowercase();
    if kw.is_empty() {
        return vec![];
    }
    let mut results = Vec::new();
    let car_pdfs = std::path::Path::new("car_pdfs");

    if let Ok(entries) = std::fs::read_dir(car_pdfs) {
        for entry in entries.flatten() {
            let path = entry.path();
            if path.is_dir() {
                let brand = entry.file_name().to_string_lossy().to_string();
                if brand_name_matches(&brand, &kw) {
                    results.push(brand);
                }
            }
        }
    }
    results
}

#[derive(Debug, Serialize)]
pub struct FileItem {
    pub name: String,
    pub path: String,
}

#[derive(Debug, Serialize)]
pub struct FolderFiles {
    pub folder: String,
    pub files: Vec<FileItem>,
}

/// 获取指定品牌（一级目录）下按二级目录分组的 PDF 文件列表
pub fn get_brand_files(brand: &str) -> Vec<FolderFiles> {
    let brand_path = std::path::Path::new("car_pdfs").join(brand);
    if !brand_path.is_dir() {
        return vec![];
    }

    let mut results = Vec::new();
    let mut root_files = Vec::new();

    if let Ok(entries) = std::fs::read_dir(&brand_path) {
        for entry in entries.flatten() {
            let path = entry.path();
            if path.is_dir() {
                let folder = entry.file_name().to_string_lossy().to_string();
                let mut files = Vec::new();
                collect_pdf_items(&path, &brand_path, &mut files);
                if !files.is_empty() {
                    results.push(FolderFiles { folder, files });
                }
            } else if let Some(ext) = path.extension() {
                if ext == "pdf" {
                    if let Some(stem) = path.file_stem() {
                        let rel_path = path.strip_prefix(&brand_path).unwrap_or(&path).to_string_lossy().to_string();
                        root_files.push(FileItem {
                            name: stem.to_string_lossy().to_string(),
                            path: rel_path,
                        });
                    }
                }
            }
        }
    }

    if !root_files.is_empty() {
        results.insert(0, FolderFiles { folder: String::new(), files: root_files });
    }
    results
}

fn collect_pdf_items(dir: &std::path::Path, base: &std::path::Path, files: &mut Vec<FileItem>) {
    if let Ok(entries) = std::fs::read_dir(dir) {
        for entry in entries.flatten() {
            let path = entry.path();
            if path.is_dir() {
                collect_pdf_items(&path, base, files);
            } else if let Some(ext) = path.extension() {
                if ext == "pdf" {
                    if let Some(stem) = path.file_stem() {
                        let rel_path = path.strip_prefix(base).unwrap_or(&path).to_string_lossy().to_string();
                        files.push(FileItem {
                            name: stem.to_string_lossy().to_string(),
                            path: rel_path,
                        });
                    }
                }
            }
        }
    }
}
