from rest_framework.test import APITestCase

from api.models import Category, Company


class CategoryViewTests(APITestCase):
    def setUp(self):
        self.company = Company.objects.create(name="A社")

    def test_list(self):
        Category.objects.create(company=self.company, name="食品")
        Category.objects.create(company=self.company, name="日用品")

        response = self.client.get("/api/categories/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 2)

    def test_retrieve(self):
        category = Category.objects.create(company=self.company, name="食品")

        response = self.client.get(f"/api/categories/{category.id}/")

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["id"], str(category.id))
        self.assertEqual(data["name"], "食品")
        self.assertEqual(data["company"], str(self.company.id))
        self.assertIsNone(data["parent_category"])

    def test_create(self):
        parent = Category.objects.create(company=self.company, name="親カテゴリ")
        payload = {
            "company": str(self.company.id),
            "name": "子カテゴリ",
            "parent_category": str(parent.id),
        }

        response = self.client.post("/api/categories/", payload, format="json")

        self.assertEqual(response.status_code, 201)
        self.assertEqual(Category.objects.count(), 2)
        created = Category.objects.get(name="子カテゴリ")
        self.assertEqual(created.company_id, self.company.id)
        self.assertEqual(created.parent_category_id, parent.id)

    def test_update(self):
        category = Category.objects.create(company=self.company, name="食品")
        payload = {
            "company": str(self.company.id),
            "name": "飲料",
            "parent_category": None,
        }

        response = self.client.put(f"/api/categories/{category.id}/", payload, format="json")

        self.assertEqual(response.status_code, 200)
        category.refresh_from_db()
        self.assertEqual(category.name, "飲料")

    def test_destroy(self):
        category = Category.objects.create(company=self.company, name="食品")

        response = self.client.delete(f"/api/categories/{category.id}/")

        self.assertEqual(response.status_code, 204)
        self.assertFalse(Category.objects.filter(id=category.id).exists())

    def test_create_duplicate_name_same_company(self):
        Category.objects.create(company=self.company, name="食品")
        payload = {
            "company": str(self.company.id),
            "name": "食品",
            "parent_category": None,
        }

        response = self.client.post("/api/categories/", payload, format="json")

        self.assertEqual(response.status_code, 400)
        self.assertEqual(Category.objects.count(), 1)

    def test_create_same_name_different_company(self):
        other_company = Company.objects.create(name="B社")
        Category.objects.create(company=self.company, name="食品")
        payload = {
            "company": str(other_company.id),
            "name": "食品",
            "parent_category": None,
        }

        response = self.client.post("/api/categories/", payload, format="json")

        self.assertEqual(response.status_code, 201)

    def test_update_same_name_without_change(self):
        category = Category.objects.create(company=self.company, name="食品")
        payload = {
            "company": str(self.company.id),
            "name": "食品",
            "parent_category": None,
        }

        response = self.client.put(f"/api/categories/{category.id}/", payload, format="json")

        self.assertEqual(response.status_code, 200)

    def test_update_duplicate_name_same_company(self):
        Category.objects.create(company=self.company, name="食品")
        daily = Category.objects.create(company=self.company, name="日用品")
        payload = {
            "company": str(self.company.id),
            "name": "食品",
            "parent_category": None,
        }

        response = self.client.put(f"/api/categories/{daily.id}/", payload, format="json")

        self.assertEqual(response.status_code, 400)
        daily.refresh_from_db()
        self.assertEqual(daily.name, "日用品")

    def test_partial_update_duplicate_name_same_company(self):
        Category.objects.create(company=self.company, name="食品")
        daily = Category.objects.create(company=self.company, name="日用品")

        response = self.client.patch(
            f"/api/categories/{daily.id}/",
            {"name": "食品"},
            format="json",
        )

        self.assertEqual(response.status_code, 400)
