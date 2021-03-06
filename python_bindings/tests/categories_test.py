import unittest


class RandomSelfTestCase(unittest.TestCase):
    def testRandomSelf(self):
        import hnswlib
        import numpy as np

        dim = 16
        num_elements = 10000

        # Generating sample data
        data = np.float32(np.random.random((num_elements, dim)))

        # Declaring index
        p = hnswlib.Index(space='l2', dim=dim)  # possible options are l2, cosine or ip

        # Initing index
        # max_elements - the maximum number of elements, should be known beforehand
        #     (probably will be made optional in the future)
        #
        # ef_construction - controls index search speed/build speed tradeoff
        # M - is tightly connected with internal dimensionality of the data
        #     stronlgy affects the memory consumption

        p.init_index(max_elements = num_elements, ef_construction = 100, M = 16, random_seed=45)

        # Controlling the recall by setting ef:
        # higher ef leads to better accuracy, but slower search
        p.set_ef(10)

        p.set_num_threads(4)  # by default using all available cores

        # We split the data in two batches:
        data1 = data[:num_elements // 2]
        data2 = data[num_elements // 2:]

        print("Adding first batch of %d elements" % (len(data1)))
        p.add_items(data1)

        p.add_tags([1, 5, 100, 33], 8)
        p.add_tags([2, 5, 66, 17], 66)
        p.add_tags(list(range(1,4000, 3)), 3)

        p.index_tagged(8)
        p.index_tagged(66)
        p.index_tagged(3, m=4)
        p.index_cross_tagged([8, 66])

        check_exception = False
        try:
            p.index_tagged(100)
        except RuntimeError as e:
            print('Correct exception:', e)
            check_exception = True
        
        self.assertTrue(check_exception, 'had not throw an exception')

        # Query the elements for themselves and measure recall:
        labels, _ = p.knn_query(data1, k=1)
        labels = np.array(labels)
        self.assertAlmostEqual(np.mean(labels.reshape(-1) == np.arange(len(data1))),1.0,3)

        # Serializing and deleting the index:
        index_path='first_half.bin'
        print("Saving index to '%s'" % index_path)
        p.save_index("first_half.bin")
        del p

        # Reiniting, loading the index
        p = hnswlib.Index(space='l2', dim=dim)  # you can change the sa

        print("\nLoading index from 'first_half.bin'\n")
        p.load_index("first_half.bin")

        self.assertIn(8, p.get_tags(5))
        self.assertIn(66, p.get_tags(5))

        print("Adding the second batch of %d elements" % (len(data2)))
        p.add_items(data2)

        p.add_tags([1011, 6015], 18)
        p.add_tags([7819], 22)

        self.assertIn(18, p.get_tags(6015))
        self.assertIn(18, p.get_tags(6015))
        
        p.reset_tags()

        p.add_tags([5], 1)
        p.add_tags([5], 2)
        p.add_tags([5], 3)

        self.assertIn(2, p.get_tags(5))
        self.assertNotIn(66, p.get_tags(5))

        # Query the elements for themselves and measure recall:
        labels, _ = p.knn_query(data, k=1)
        labels = np.array(labels)
        self.assertAlmostEqual(np.mean(labels.reshape(-1) == np.arange(len(data))),1.0,3)


if __name__ == "__main__":
    unittest.main()