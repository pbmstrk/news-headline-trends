resource "google_storage_bucket" "data_backup" {
  name                        = "news_headline_trends_data_backup"
  location                    = "EU"
  uniform_bucket_level_access = true
  public_access_prevention    = "enforced"
}